#!/usr/bin/env python3
"""Run several roadmap tickets at once in the main checkout, alone or as a group of issues (TKT-16, TKT-20).

Usage, from the main checkout:
    python3 .claude/scripts/tickets.py check --ticket T0.10 [--force]     (prints nothing when the ticket may start)
    python3 .claude/scripts/tickets.py list
    python3 .claude/scripts/tickets.py resolve [--json] <refs>
    python3 .claude/scripts/tickets.py approve <refs>                      (the person's approval of a group's plans)
    python3 .claude/scripts/tickets.py next [--json] <refs>
    python3 .claude/scripts/tickets.py watch <refs> [--every 120] [--once]
    python3 .claude/scripts/tickets.py prune
    python3 .claude/scripts/tickets.py setup

Every running ticket shares the main checkout and the branch ``feature/tickets``; its files live in
``docs/tickets/<ID>/`` and its state in ``.git/swarm/<ID>/``. A ticket started before TKT-16 shared the checkout keeps
its own worktree on ``feature/<ID>`` until ``prune`` removes it once merged.

- ``check`` applies the start rule (TKT-16) and prints one problem per line: a prerequisite of
  ``docs/specs/roadmap/gantt/ticket-graph.json`` that is not done (merged on ``origin/develop``, or committed on
  ``feature/tickets`` with its pull request open), an open ticket that changes one of the same areas, or a field ticket
  whose campaign has not flown. It exits 1 when it prints anything, unless ``--force``.
- ``list`` prints the open tickets, the files each owns and its areas.
- **Groups** (TKT-20). ``<refs>`` are issue numbers (``#12``: a ticket, or an epic or a phase with every ticket under
  it, through the sub-issues of ``.claude/github.json``), ticket IDs (``T0.10``), epic IDs (``E0.4``) or phase IDs
  (``P1``), separated by spaces. Merged tickets are left out; the rest are ordered by their prerequisites.
  - ``resolve`` prints each ticket with its state, the prerequisites it waits for and whether it may start now.
  - ``approve`` approves, for the person, every plan of the group that awaits approval and passes ``check_plan.py``:
    ``**Plan:** 🟢 Approved``, an event in ``PROGRESS.md``, the card moved. The PreToolUse hook asks the person before
    Claude runs it.
  - ``next`` prints the approved tickets of the group that may start now.
  - ``watch`` prints an exhaustive report of the group every ``--every`` seconds, with a ``▶️ CAN START <ID>`` line
    for each ticket that may start, and ends when the group is merged or waits for the person.
- ``prune`` removes the merged legacy worktrees and their empty folder, brings ``develop`` up to date, and puts the
  main checkout back on ``develop`` once no ticket is open and ``feature/tickets`` is merged.
- ``setup`` turns on the GitFlow git hooks of ``.githooks/`` for this clone (TKT-15).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))

from roadmap_gantt import areas, key, roadmap_rows
from ticket_tree import (
    BRANCH_PREFIX,
    DEVELOP,
    REMOTE,
    SHARED_BRANCH,
    TICKET_SUBJECT,
    git,
    has_remote,
    is_clean,
    load_state,
    main_checkout,
    open_states,
    ticket_paths,
    worktrees,
)

SCRIPTS = Path(__file__).resolve().parent
REPOSITORY = SCRIPTS.parents[1]
GRAPH_ENV = "SWARM_TICKET_GRAPH"
CHECK_PLAN_ENV = "SWARM_CHECK_PLAN"
CLOSED_ENV = "SWARM_CLOSED_ISSUES"
GRAPH = Path("docs/specs/roadmap/gantt/ticket-graph.json")
GITHUB_STATE = Path(".claude/github.json")
HOOKS_PATH = ".githooks"
TICKET_ID = re.compile(r"^T\d+\.\d{2}$")
EPIC_ID = re.compile(r"^E\d+\.\d+$")
PHASE_ID = re.compile(r"^P\d+$")
ISSUE_REF = re.compile(r"^#(\d+)$")
TASK_ID = re.compile(r'"id":\s*"K\d+"')
GIT_CONFIG = {"core.hooksPath": HOOKS_PATH, "push.autoSetupRemote": "true", "fetch.prune": "true"}
PLAN_AWAITING = "**Plan:** 🟡 Awaiting approval"
PLAN_APPROVED = "**Plan:** 🟢 Approved"
PUSH_AWAITING = "**Push:** 🟡"
STATES = [
    ("merged", "🏁", "merged"),
    ("review", "👀", "in review"),
    ("code_review", "🔍", "awaits your code review"),
    ("running", "🔄", "running"),
    ("approved", "✅", "approved"),
    ("planned", "📝", "plan awaits approval"),
    ("no_plan", "⬜", "no plan"),
]
ICON = {name: icon for name, icon, _ in STATES}
LABEL = {name: label for name, _, label in STATES}


######################
# Repository reading #
######################


def graph(main: Path) -> Dict[str, Dict[str, object]]:
    path = Path(os.environ.get(GRAPH_ENV, str(main / GRAPH)))
    return json.loads(path.read_text(encoding="utf-8"))["tickets"]


def develop_ref(main: Path, fetch: bool = False) -> str:
    """Return ``origin/develop`` when the remote has it (fetched first when asked), else ``develop``."""
    if has_remote(main):
        if fetch:
            git(main, "fetch", "--quiet", REMOTE, DEVELOP, check=False)
        if git(main, "rev-parse", "--verify", "--quiet", f"{REMOTE}/{DEVELOP}", check=False)[0] == 0:
            return f"{REMOTE}/{DEVELOP}"
    return DEVELOP


def merged_tickets(main: Path, ref: str) -> Set[str]:
    """Return the tickets merged on ``ref``: those whose ``EXPLAIN.md`` is committed there (TKT-14)."""
    names = git(main, "ls-tree", "-r", "--name-only", ref, "docs/tickets", check=False)[1].splitlines()
    return {name.split("/")[2] for name in names if name.endswith("/EXPLAIN.md")}


def finished_tickets(main: Path, ref: str) -> Set[str]:
    """Return the tickets committed, but not merged yet: on ``feature/tickets`` or on a legacy ``feature/<ID>``."""
    found: Set[str] = set()
    branches = git(main, "for-each-ref", "--format=%(refname:short)", f"refs/heads/{BRANCH_PREFIX}", check=False)[1]
    for branch in branches.splitlines():
        legacy = branch[len(BRANCH_PREFIX) :]
        subjects = git(main, "log", "--format=%s", f"{ref}..{branch}", check=False)[1].splitlines()
        if branch == SHARED_BRANCH:
            found |= {m.group(1) for m in map(TICKET_SUBJECT.match, subjects) if m}
        elif TICKET_ID.match(legacy) and subjects:
            found.add(legacy)
    return found


def open_tickets(main: Path) -> Dict[str, Path]:
    """Return every running ticket with its home: the main checkout, or a worktree from before TKT-16."""
    found: Dict[str, Path] = {ticket: main for ticket in open_states(main)}
    for path, branch in worktrees(main):
        legacy = branch[len(BRANCH_PREFIX) :] if branch.startswith(BRANCH_PREFIX) else ""
        if TICKET_ID.match(legacy):
            found[legacy] = path
    return dict(sorted(found.items(), key=lambda item: key(item[0])))


def folder_of(main: Path, ticket: str) -> Path:
    home = open_tickets(main).get(ticket, main)
    return home / "docs" / "tickets" / ticket


ROADMAP_TITLES: Dict[str, str] = {}


def title_of(main: Path, ticket: str) -> str:
    """Return the title of the ticket's TICKET.md, or of its row on the roadmap before it is planned."""
    path = folder_of(main, ticket) / "TICKET.md"
    if path.is_file():
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.startswith("# "):
                return line[2:].split(":", 1)[-1].strip()
    if not ROADMAP_TITLES:
        try:
            ROADMAP_TITLES.update({ident: row["title"] for ident, row in roadmap_rows().items()})
        except (OSError, ValueError) as error:
            print(f"note: roadmap titles unavailable ({type(error).__name__})", file=sys.stderr)
    return ROADMAP_TITLES.get(ticket, "")


def plan_state(main: Path, ticket: str) -> str:
    plan = folder_of(main, ticket) / "PLAN.md"
    if not plan.is_file():
        return "no_plan"
    text = plan.read_text(encoding="utf-8")
    if PUSH_AWAITING in text:
        return "code_review"
    return "approved" if PLAN_APPROVED in text else "planned"


##############
# Start rule #
##############


def problems(main: Path, ticket: str, done: Optional[Set[str]] = None) -> List[str]:
    """Return why a ticket may not start yet (TKT-16), one sentence each."""
    tickets = graph(main)
    if ticket not in tickets:
        return [f"{ticket} is not in the ticket graph: add it to {GRAPH} first."]
    info = tickets[ticket]
    if done is None:
        ref = develop_ref(main, fetch=True)
        done = merged_tickets(main, ref) | finished_tickets(main, ref)
    found: List[str] = []
    waiting = [dep for dep in info.get("deps", []) if dep not in done]  # type: ignore[union-attr]
    if waiting:
        found.append(
            f"{', '.join(waiting)} not done yet (merged, or committed on {SHARED_BRANCH}): "
            f"{ticket} builds on {'it' if len(waiting) == 1 else 'them'}."
        )
    field = info.get("field")
    if isinstance(field, dict):
        found.append(
            f"{ticket} fixes what {field.get('after')} finds: it starts once that has flown ({field.get('start')})."
        )
    mine = areas(str(info.get("area", "")))
    for other, home in open_tickets(main).items():
        if other == ticket or other in done:
            continue
        theirs = areas(str(tickets.get(other, {}).get("area", "")))
        shared = sorted((mine & theirs) or (mine | theirs if "*" in mine or "*" in theirs else set()))
        if shared:
            found.append(f"{other} is open in {home} and changes {', '.join(shared)}: wait for it (area lock).")
    return found


##########
# Groups #
##########


def github_state(main: Path) -> Dict[str, object]:
    path = main / GITHUB_STATE
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {"issues": {}, "subissues": []}


def expand(ident: str, children: Dict[str, List[str]]) -> List[str]:
    if TICKET_ID.match(ident):
        return [ident]
    found: List[str] = []
    for child in children.get(ident, []):
        found.extend(expand(child, children))
    return found


def closed_issues(main: Path, state: Dict[str, object]) -> Set[int]:
    """Return the numbers of the closed issues of the repository: a ticket closed on GitHub is done (TKT-20).

    ``SWARM_CLOSED_ISSUES`` (comma-separated numbers) replaces the question to GitHub, for tests; without it and
    without GitHub (no ``repo`` in ``.claude/github.json``, ``gh`` missing or offline), no issue counts as closed.
    """
    given = os.environ.get(CLOSED_ENV)
    if given is not None:
        return {int(n) for n in given.split(",") if n.strip().isdigit()}
    repo = state.get("repo")
    if not isinstance(repo, str):
        return set()
    result = subprocess.run(
        [
            "gh",
            "issue",
            "list",
            "-R",
            repo,
            "--state",
            "closed",
            "--limit",
            "1000",
            "--json",
            "number",
            "--jq",
            ".[].number",
        ],
        cwd=main,
        capture_output=True,
        text=True,
        check=False,
    )
    return {int(n) for n in result.stdout.split() if n.isdigit()} if result.returncode == 0 else set()


def resolve(main: Path, refs: List[str]) -> List[str]:
    """Return the tickets of a group, merged ones left out, every prerequisite before the tickets that need it."""
    state = github_state(main)
    issues = state.get("issues", {})
    by_number = {int(v["number"]): k for k, v in issues.items() if isinstance(v, dict) and "number" in v}  # type: ignore[union-attr]
    children: Dict[str, List[str]] = {}
    for parent, child in state.get("subissues", []):  # type: ignore[union-attr]
        children.setdefault(str(parent), []).append(str(child))
    tickets = graph(main)
    wanted: List[str] = []
    for ref in refs:
        issue = ISSUE_REF.match(ref)
        ident = by_number.get(int(issue.group(1))) if issue else ref
        if ident is None or not (TICKET_ID.match(ident) or EPIC_ID.match(ident) or PHASE_ID.match(ident)):
            raise SystemExit(f"Unknown reference {ref}: use #<issue>, T0.10, E0.4 or P1.")
        found = expand(ident, children)
        if not found:
            raise SystemExit(f"{ref} ({ident}) holds no ticket: run python3 .claude/scripts/board.py bootstrap first.")
        wanted.extend(ticket for ticket in found if ticket not in wanted)
    merged = merged_tickets(main, develop_ref(main))
    closed = closed_issues(main, state)
    numbers = {k: int(v["number"]) for k, v in issues.items() if isinstance(v, dict) and "number" in v}  # type: ignore[union-attr]
    done = merged | {ticket for ticket in wanted if numbers.get(ticket) in closed}
    left = sorted((ticket for ticket in wanted if ticket not in done), key=key)
    ordered: List[str] = []
    while left:
        ready = [t for t in left if not any(d in left for d in tickets.get(t, {}).get("deps", []))]  # type: ignore[union-attr]
        step = ready[0] if ready else left[0]
        ordered.append(step)
        left.remove(step)
    return ordered


def rows(main: Path, group: List[str]) -> List[Dict[str, object]]:
    """Return the state of every ticket of a group."""
    ref = develop_ref(main, fetch=True)
    merged = merged_tickets(main, ref)
    finished = finished_tickets(main, ref)
    done = merged | finished
    running = open_tickets(main)
    tickets = graph(main)
    found: List[Dict[str, object]] = []
    for ticket in group:
        if ticket in merged:
            state = "merged"
        elif ticket in finished:
            state = "review"
        elif ticket in running:
            state = "code_review" if plan_state(main, ticket) == "code_review" else "running"
        else:
            state = plan_state(main, ticket)
        blockers = problems(main, ticket, done) if state == "approved" else []
        deps = [d for d in tickets.get(ticket, {}).get("deps", []) if d not in done]  # type: ignore[union-attr]
        found.append(
            {
                "ticket": ticket,
                "state": state,
                "title": title_of(main, ticket),
                "waits_for": deps,
                "can_start": state == "approved" and not blockers,
                "problems": blockers,
            }
        )
    return found


def show_rows(found: List[Dict[str, object]]) -> None:
    for row in found:
        state = str(row["state"])
        waits = f" · ⛓️ waits for {', '.join(row['waits_for'])}" if row["waits_for"] else ""  # type: ignore[arg-type]
        start = " · ▶️ may start" if row["can_start"] else ""
        print(f"{ICON[state]} {row['ticket']}  {str(row['title'])[:60]} · {LABEL[state]}{waits}{start}")


def check_plan_passes(main: Path, ticket: str) -> bool:
    command = os.environ.get(CHECK_PLAN_ENV)
    if command:
        args = shlex.split(command)
    else:
        args = [
            sys.executable,
            str(REPOSITORY / ".claude/skills/ticket/scripts/check_plan.py"),
            ticket,
            "--root",
            str(main),
        ]
    result = subprocess.run(args, cwd=main, capture_output=True, text=True, check=False)
    return result.returncode == 0 and not result.stdout.strip()


def approve(main: Path, group: List[str]) -> int:
    failed = 0
    for row in rows(main, group):
        ticket = str(row["ticket"])
        if row["state"] != "planned":
            continue
        folder = folder_of(main, ticket)
        if not check_plan_passes(main, ticket):
            print(f"❌ {ticket}: PLAN.md fails check_plan.py, left awaiting approval.")
            failed += 1
            continue
        plan = folder / "PLAN.md"
        plan.write_text(plan.read_text(encoding="utf-8").replace(PLAN_AWAITING, PLAN_APPROVED, 1), encoding="utf-8")
        progress = folder / "PROGRESS.md"
        if progress.is_file():
            text = progress.read_text(encoding="utf-8")
            row = f"| {datetime.now().strftime('%Y-%m-%d %H:%M')} | Plan approved by the person (group approval) | 👤 person | 🟢 Approved |"
            marker = "| --- | --- | --- | --- |"
            if marker in text:
                head, tail = text.split(marker, 1)
                body, rest = (tail.split("\n\n", 1) + [""])[:2]
                text = f"{head}{marker}{body.rstrip()}\n{row}\n\n{rest}".rstrip() + "\n"
            progress.write_text(text, encoding="utf-8")
        if main.resolve() == REPOSITORY.resolve():
            subprocess.run(
                [sys.executable, str(SCRIPTS / "board.py"), "move", "--ticket", ticket, "--status", "planned"],
                cwd=main,
                capture_output=True,
                check=False,
            )
        print(f"🟢 {ticket}: plan approved")
    return 1 if failed else 0


def pull_request_line(main: Path, ticket: str) -> str:
    """Return the pull request holding a finished ticket and its checks, when GitHub can be asked."""
    if not has_remote(main):
        return ""
    branch = (
        SHARED_BRANCH if ticket in open_states(main) or ticket not in open_tickets(main) else f"{BRANCH_PREFIX}{ticket}"
    )
    result = subprocess.run(
        [
            "gh",
            "pr",
            "list",
            "--head",
            branch,
            "--state",
            "open",
            "--json",
            "number,headRefOid",
            "--jq",
            '.[0] | "\\(.number) \\(.headRefOid)"',
        ],
        cwd=main,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0 or not result.stdout.strip() or result.stdout.strip() == "null":
        return ""
    number, sha = result.stdout.split()
    runs = subprocess.run(
        [
            "gh",
            "api",
            f"repos/{{owner}}/{{repo}}/commits/{sha}/check-runs?per_page=100",
            "--jq",
            '[.check_runs[] | (.conclusion // "pending")] | group_by(.) | map("\\(.[0])=\\(length)") | join(" ")',
        ],
        cwd=main,
        capture_output=True,
        text=True,
        check=False,
    )
    tally = dict(part.split("=") for part in runs.stdout.split()) if runs.returncode == 0 else {}
    return (
        f" · #{number} ✅{tally.get('success', 0)} ❌{tally.get('failure', 0)} "
        f"⏳{tally.get('pending', 0)} ⏭️{tally.get('skipped', 0)}"
    )


def report(main: Path, refs: List[str], group: List[str]) -> Tuple[str, List[str], bool]:
    """Return the group report, the tickets that may start, and whether the watch should end."""
    found = rows(main, group)
    tickets = graph(main)
    counts = " · ".join(f"{icon} {label} {sum(1 for r in found if r['state'] == name)}" for name, icon, label in STATES)
    out = [
        f"━━━━━━━━━━ 🕒 {datetime.now().strftime('%H:%M:%S')} · 🎫 Group {' '.join(refs)} · {len(found)} tickets ━━━━━━━━━━",
        f"📊 {counts}",
    ]
    for row in found:
        ticket, state = str(row["ticket"]), str(row["state"])
        detail = LABEL[state]
        if state in ("running", "code_review"):
            plan = folder_of(main, ticket) / "PLAN.md"
            total = len(TASK_ID.findall(plan.read_text(encoding="utf-8"))) if plan.is_file() else 0
            done_tasks = len(load_state(main, ticket).get("integrated") or [])  # type: ignore[arg-type]
            detail += f" · 🧩 {done_tasks}/{total or '?'} tasks · 📄 {len(ticket_paths(load_state(main, ticket), ticket))} files"
        if state == "review":
            detail += pull_request_line(main, ticket)
        if row["waits_for"]:
            detail += f" · ⛓️ waits for {', '.join(row['waits_for'])}"  # type: ignore[arg-type]
        if row["problems"] and not row["can_start"]:
            detail += f" · ✋ {str(row['problems'][0])[:90]}"  # type: ignore[index]
        area = ", ".join(sorted(areas(str(tickets.get(ticket, {}).get("area", "")))))
        out.append(f"   {ICON[state]} {ticket}  {str(row['title'])[:50]} · {detail} · 🗂️ {area}")
    startable = [str(r["ticket"]) for r in found if r["can_start"]]
    out.extend(f"▶️ CAN START {ticket}" for ticket in startable)
    moving = any(r["state"] in ("running", "review") for r in found) or startable
    finished = all(r["state"] == "merged" for r in found)
    if finished:
        out.append("🏁 Every ticket of the group is merged.")
    elif not moving:
        waiting = [f"{r['ticket']} ({LABEL[str(r['state'])]})" for r in found if r["state"] != "merged"]
        out.append(f"✋ Waiting for the person: {', '.join(waiting)}")
    return "\n".join(out), startable, finished or not moving


###########
# Commands #
###########


def show_list(main: Path) -> None:
    running = open_tickets(main)
    if not running:
        print("No open ticket. Start one with /ticket-plan <ID> or a group with /issue-plan <refs>.")
        return
    tickets = graph(main)
    print(f"🎫 {len(running)} open ticket(s) on {git(main, 'branch', '--show-current')[1]}")
    for ticket, home in running.items():
        owned = len(ticket_paths(load_state(main, ticket), ticket)) if home == main else 0
        files = f"{owned} files" if home == main else f"own worktree {home} (before TKT-16)"
        area = ", ".join(sorted(areas(str(tickets.get(ticket, {}).get("area", "")))))
        print(f"  🔄 {ticket}  {title_of(main, ticket)[:60]} · 📄 {files} · 🗂️ {area}")


def prune(main: Path) -> None:
    """Remove the merged legacy worktrees, bring develop up to date, and leave feature/tickets once all is merged."""
    ref = develop_ref(main, fetch=True)
    merged = merged_tickets(main, ref)
    for path, branch in worktrees(main):
        ticket = branch[len(BRANCH_PREFIX) :] if branch.startswith(BRANCH_PREFIX) else ""
        if not TICKET_ID.match(ticket) or ticket not in merged:
            continue
        if git(main, "merge-base", "--is-ancestor", branch, ref, check=False)[0] != 0 or not is_clean(path):
            print(f"⚠️  {ticket} is merged but {path} has more work: kept.")
            continue
        git(main, "worktree", "remove", "--force", str(path))
        git(main, "branch", "-D", branch, check=False)
        print(f"🧹 {ticket}: its own worktree and branch removed")
        if path.parent.is_dir() and not any(path.parent.iterdir()):
            path.parent.rmdir()
            print(f"🧹 {path.parent} removed")
    branch = git(main, "branch", "--show-current")[1]
    if ref != DEVELOP and branch != DEVELOP:
        git(main, "fetch", "--quiet", REMOTE, f"{DEVELOP}:{DEVELOP}", check=False)
    shared_merged = git(main, "merge-base", "--is-ancestor", SHARED_BRANCH, ref, check=False)[0] == 0
    if branch == SHARED_BRANCH and not open_states(main) and shared_merged and is_clean(main):
        git(main, "checkout", "--quiet", DEVELOP)
        git(main, "branch", "-D", SHARED_BRANCH, check=False)
        print(f"🏁 Every ticket is merged: the main checkout is back on {DEVELOP}")
        branch = DEVELOP
    up_to_date = branch == DEVELOP and ref != DEVELOP and is_clean(main)
    if up_to_date and git(main, "merge", "--ff-only", "--quiet", ref, check=False)[0] == 0:
        print(f"⏩ {DEVELOP} is up to date with {ref}")


def setup(main: Path) -> None:
    for name, value in GIT_CONFIG.items():
        git(main, "config", name, value)
    print(f"🪝 GitFlow hooks on ({HOOKS_PATH}/), push sets its upstream, fetch prunes deleted branches")


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    check = sub.add_parser("check")
    check.add_argument("--ticket", required=True)
    check.add_argument("--force", action="store_true")
    for name in ("resolve", "next"):
        group = sub.add_parser(name)
        group.add_argument("--json", action="store_true")
        group.add_argument("refs", nargs="+")
    sub.add_parser("approve").add_argument("refs", nargs="+")
    watch = sub.add_parser("watch")
    watch.add_argument("refs", nargs="+")
    watch.add_argument("--every", type=int, default=120)
    watch.add_argument("--once", action="store_true")
    for name in ("list", "prune", "setup"):
        sub.add_parser(name)
    args = parser.parse_args(argv)
    top = Path(git(Path.cwd(), "rev-parse", "--show-toplevel")[1])
    main_dir = main_checkout(top)
    if args.command == "check":
        found = problems(main_dir, args.ticket)
        for problem in found:
            print(problem)
        return 1 if found and not args.force else 0
    if args.command == "resolve":
        found = rows(main_dir, resolve(main_dir, args.refs))
        if args.json:
            print(json.dumps(found, ensure_ascii=False))
        elif not found:
            print(f"🏁 Every ticket of {' '.join(args.refs)} is merged or closed: nothing to do.")
        else:
            show_rows(found)
    elif args.command == "next":
        startable = [str(r["ticket"]) for r in rows(main_dir, resolve(main_dir, args.refs)) if r["can_start"]]
        print(json.dumps(startable)) if args.json else print("\n".join(startable))
    elif args.command == "approve":
        return approve(main_dir, resolve(main_dir, args.refs))
    elif args.command == "watch":
        group = resolve(main_dir, args.refs)
        while True:
            text, _, ended = report(main_dir, args.refs, group)
            print(text, flush=True)
            if args.once or ended:
                return 0
            time.sleep(args.every)
    elif args.command == "list":
        show_list(main_dir)
    elif args.command == "prune":
        prune(main_dir)
    else:
        setup(main_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
