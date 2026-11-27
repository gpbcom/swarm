#!/usr/bin/env python3
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

sys.path[:0] = [str(Path(__file__).resolve().parents[1] / group) for group in ("tickets", "github", "reports")]

import branches
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

USAGE = """Run several roadmap tickets at once in the main checkout, alone or as a group of issues (TKT-16, TKT-20).

Usage, from the main checkout:
    python3 .claude/scripts/tickets/tickets.py check --ticket T0.10 [--force]     (prints nothing when the ticket may start)
    python3 .claude/scripts/tickets/tickets.py list
    python3 .claude/scripts/tickets/tickets.py resolve [--json] <refs>
    python3 .claude/scripts/tickets/tickets.py approve <refs>                      (the person's approval of a group's plans)
    python3 .claude/scripts/tickets/tickets.py next [--json] <refs>
    python3 .claude/scripts/tickets/tickets.py watch <refs> [--every 120] [--once]
    python3 .claude/scripts/tickets/tickets.py branches
    python3 .claude/scripts/tickets/tickets.py prune [--dry-run]
    python3 .claude/scripts/tickets/tickets.py setup

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
- ``branches`` gives every branch, local and on GitHub, its verdict against ``origin/develop`` (TKT-25): 🔒
  protected (``master`` changes only through a release pull request), 🔄 open, 🧹 merged, integrated or superseded
  (delete, never rebase), 🌱 live (the only ones to rebase). See ``branches.py``.
- ``prune`` removes the merged legacy worktrees and their empty folder, brings ``develop`` up to date, puts the main
  checkout back on ``develop`` once no ticket is open and ``feature/tickets`` is merged, then deletes every 🧹 branch
  (locally and on GitHub), its worktree and the leftover ticket folders, after writing them all, uncommitted work
  included, to a bundle in ``.git/swarm/backups/`` (TKT-25). ``--dry-run`` only says what it would delete.
- ``setup`` turns on the GitFlow git hooks of ``.githooks/`` for this clone (TKT-15).
"""

SCRIPTS = Path(__file__).resolve().parent
REPOSITORY = SCRIPTS.parents[2]
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
PLAN_JSON = re.compile(r"^```json[ \t]*\n(.*?)^```[ \t]*$", re.MULTILINE | re.DOTALL)
LANGUAGES = ("en", "fr", "de", "es")
PYTHON_LOCALES = "backend/swarm-storage/src/swarm_storage/shared/i18n/locales"
# L-51: the files every ticket appends to, whatever its area: the lock files and the message catalogues. ``integrate``
# gives a file to one open ticket only, so two open tickets whose plans list one of them can never both pass their
# checks: a ticket waits while another open ticket's plan lists one of its shared files (TKT-16). check_plan.py makes
# the task that changes a manifest own its lock file, so that the plan lists it.
SHARED_FILES = (
    "pnpm-lock.yaml",
    "uv.lock",
    "rust/Cargo.lock",
    "frontend/apps/desktop/src-tauri/Cargo.lock",
    *(f"frontend/packages/i18n/src/messages/{language}.json" for language in LANGUAGES),
    f"{PYTHON_LOCALES}/swarm.pot",
    *(f"{PYTHON_LOCALES}/{language}/LC_MESSAGES/swarm.po" for language in LANGUAGES),
)
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


def plan_tasks(main: Path, ticket: str) -> List[Dict[str, object]]:
    """Return the tasks of the json block of the ticket's PLAN.md, or an empty list without a readable one."""
    plan = folder_of(main, ticket) / "PLAN.md"
    if not plan.is_file():
        return []
    for block in reversed(PLAN_JSON.findall(plan.read_text(encoding="utf-8"))):
        try:
            tasks = json.loads(block)
        except json.JSONDecodeError:
            continue
        if isinstance(tasks, list) and all(isinstance(task, dict) for task in tasks):
            return tasks
    return []


def plan_task_ids(main: Path, ticket: str) -> List[str]:
    """Return the distinct task ids of the ticket's plan, in order."""
    return list(dict.fromkeys(str(task.get("id")) for task in plan_tasks(main, ticket) if task.get("id")))


def shared_files(main: Path, ticket: str) -> Set[str]:
    """Return the shared files (L-51) the ticket's plan lists in its tasks' files, or that its state already owns."""
    listed: Set[str] = set()
    for task in plan_tasks(main, ticket):
        files = task.get("files")
        if isinstance(files, list):
            listed.update(str(path) for path in files)
    state = load_state(main, ticket)
    owned = state.get("paths")
    if isinstance(owned, list):
        listed.update(str(path) for path in owned)
    return {path for path in listed if path in SHARED_FILES}


##############
# Start rule #
##############


def shared_areas(mine: Set[str], theirs: Set[str]) -> List[str]:
    """Return the areas two tickets both change (``*`` overlaps every area), sorted."""
    return sorted((mine & theirs) or (mine | theirs if "*" in mine or "*" in theirs else set()))


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
    running = open_tickets(main)
    if ticket in running:
        return found
    for other, home in running.items():
        if other in done:
            continue
        theirs = areas(str(tickets.get(other, {}).get("area", "")))
        shared = shared_areas(mine, theirs)
        if shared:
            found.append(f"{other} is open in {home} and changes {', '.join(shared)}: wait for it (area lock).")
        both = sorted(shared_files(main, ticket) & shared_files(main, other))
        if both:
            found.append(
                f"{other} is open in {home} and its plan lists {', '.join(both)}, which {ticket}'s plan lists too: "
                f"wait for it (shared file lock)."
            )
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


def done_tickets(main: Path, fetch: bool = False) -> Dict[str, str]:
    """Return every ticket that needs no more work, with why: THE definition of done of the harness (TKT-23).

    A ticket is done when it is merged on ``origin/develop`` (its ``EXPLAIN.md`` is there, TKT-14) or when its issue is
    closed on GitHub (done another way, or not planned). Every command that acts on tickets skips these.
    """
    state = github_state(main)
    found = {
        ticket: f"merged on {develop_ref(main, fetch)}" for ticket in merged_tickets(main, develop_ref(main, fetch))
    }
    closed = closed_issues(main, state)
    for ticket, issue in state.get("issues", {}).items():  # type: ignore[union-attr]
        if TICKET_ID.match(ticket) and isinstance(issue, dict) and issue.get("number") in closed:
            found.setdefault(ticket, f"its issue #{issue['number']} is closed on GitHub")
    return found


def finished_reason(main: Path, ticket: str) -> str:
    """Return why a ticket needs no more work (done, or finished with its pull request open), or an empty string."""
    done = done_tickets(main, fetch=True)
    if ticket in done:
        return f"{ticket} is already done ({done[ticket]}): there is nothing to plan or run."
    if ticket in finished_tickets(main, develop_ref(main)):
        return f"{ticket} is already finished: its commit waits in the pull request of {SHARED_BRANCH}."
    return ""


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
            raise SystemExit(
                f"{ref} ({ident}) holds no ticket: run python3 .claude/scripts/github/board.py bootstrap first."
            )
        wanted.extend(ticket for ticket in found if ticket not in wanted)
    done = done_tickets(main)
    left = sorted((ticket for ticket in wanted if ticket not in done), key=key)
    ordered: List[str] = []
    while left:
        ready = [t for t in left if not any(d in left for d in tickets.get(t, {}).get("deps", []))]  # type: ignore[union-attr]
        step = ready[0] if ready else left[0]
        ordered.append(step)
        left.remove(step)
    return ordered


def without_overlaps(main: Path, startable: List[str]) -> List[str]:
    """Keep, in order, the tickets whose areas overlap no earlier kept one: the others wait for the next call."""
    tickets = graph(main)
    kept: List[str] = []
    for ticket in startable:
        mine = areas(str(tickets.get(ticket, {}).get("area", "")))
        clash = [o for o in kept if shared_areas(mine, areas(str(tickets.get(o, {}).get("area", ""))))]
        if clash:
            print(f"note: {ticket} waits for {clash[0]}, which starts now and changes the same area.", file=sys.stderr)
            continue
        files = shared_files(main, ticket)
        clash = [o for o in kept if files & shared_files(main, o)]
        if clash:
            both = ", ".join(sorted(files & shared_files(main, clash[0])))
            print(f"note: {ticket} waits for {clash[0]}, which starts now and also lists {both}.", file=sys.stderr)
            continue
        kept.append(ticket)
    return kept


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
                [
                    sys.executable,
                    str(SCRIPTS.parent / "github" / "board.py"),
                    "move",
                    "--ticket",
                    ticket,
                    "--status",
                    "planned",
                ],
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
            # L-49: a task integrated again after its fix (TKT-6, TKT-19) is one task: count the plan's distinct ids.
            planned = plan_task_ids(main, ticket)
            total = len(planned)
            integrated = {str(task) for task in load_state(main, ticket).get("integrated") or []}  # type: ignore[union-attr]
            done_tasks = len(integrated & set(planned))
            detail += f" · 🧩 {done_tasks}/{total or '?'} tasks · 📄 {len(ticket_paths(load_state(main, ticket), ticket))} files"
            refused = load_state(main, ticket).get("refused")
            if isinstance(refused, list) and refused:
                detail += f" · ⚠️ {len(refused)} change(s) refused: another open ticket owns the file (L-51)"
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


def branch_verdicts(main: Path, fetch: bool) -> Tuple[str, List[branches.Verdict]]:
    """Return the develop reference and the verdict of every branch and leftover ticket folder (TKT-25)."""
    if fetch and has_remote(main):
        git(main, "fetch", "--quiet", "--prune", REMOTE, check=False)
    ref = develop_ref(main)
    done = set(done_tickets(main))
    return ref, branches.classify(main, ref, done, set(open_tickets(main)))


def prune(main: Path, dry_run: bool = False) -> None:
    """Remove the merged legacy worktrees, bring develop up to date, leave feature/tickets once all is merged, then
    delete every branch whose work develop holds, after a backup (TKT-25)."""
    if dry_run:
        branches.clean(main, branch_verdicts(main, fetch=True)[1], dry_run=True)
        return
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
    branches.clean(main, branch_verdicts(main, fetch=True)[1], dry_run=False)


def setup(main: Path) -> None:
    for name, value in GIT_CONFIG.items():
        git(main, "config", name, value)
    print(f"🪝 GitFlow hooks on ({HOOKS_PATH}/), push sets its upstream, fetch prunes deleted branches")


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=USAGE.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    done_command = sub.add_parser("done")
    done_command.add_argument("--ticket", required=True)
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
    for name in ("list", "branches", "setup"):
        sub.add_parser(name)
    sub.add_parser("prune").add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    top = Path(git(Path.cwd(), "rev-parse", "--show-toplevel")[1])
    main_dir = main_checkout(top)
    if args.command == "done":
        reason = finished_reason(main_dir, args.ticket)
        if reason:
            print(reason)
        return 0 if reason else 1
    if args.command == "check":
        reason = finished_reason(main_dir, args.ticket)
        if reason:
            print(reason)
            return 1
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
        startable = without_overlaps(main_dir, startable)
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
    elif args.command == "branches":
        ref, verdicts = branch_verdicts(main_dir, fetch=True)
        branches.show(verdicts, ref)
    elif args.command == "prune":
        prune(main_dir, args.dry_run)
    else:
        setup(main_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
