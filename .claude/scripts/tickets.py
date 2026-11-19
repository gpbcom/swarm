#!/usr/bin/env python3
"""Run several roadmap tickets at once: the start rule, the open tickets, their clean-up and VS Code (TKT-16).

Usage, from the main checkout or any ticket's worktree:
    python3 .claude/scripts/tickets.py check --ticket T0.09 [--force]   (prints nothing when the ticket may start)
    python3 .claude/scripts/tickets.py list [--remote]
    python3 .claude/scripts/tickets.py prune
    python3 .claude/scripts/tickets.py workspace
    python3 .claude/scripts/tickets.py setup

- ``check`` applies the start rule of TKT-16 and prints one problem per line: a prerequisite of
  ``docs/specs/roadmap/gantt/ticket-graph.json`` that is not merged on ``develop`` (``origin/develop`` with a remote;
  a ticket is merged when its ``EXPLAIN.md`` is there, TKT-14), an open ticket that changes one of the same areas (a
  service, a front end, a package), or a field ticket whose campaign has not flown. It exits 1 when it prints
  anything, unless ``--force``, which the person gives on purpose (``/ticket-run T0.09 --force``).
- ``list`` prints every open ticket (each worktree on a ``feature/<ID>`` branch): its state, tasks integrated, areas,
  and with ``--remote`` its pull request and checks.
- ``prune`` removes the worktree and the local branch of every ticket merged on ``develop``, fast-forwards the main
  checkout's ``develop`` when it is clean, and rewrites the VS Code workspace.
- ``workspace`` writes ``swarm.code-workspace`` (not versioned) at the root of the main checkout: ``develop`` and
  every open ticket side by side, so that VS Code's Source Control shows the live, uncommitted work of every ticket at
  once, with the extensions that show the pull requests, the board and the branch graph.
- ``setup`` turns on the GitFlow git hooks of ``.githooks/`` for this clone (TKT-15).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))

from roadmap_gantt import areas, key
from ticket_tree import (
    BRANCH_PREFIX,
    DEVELOP,
    REMOTE,
    git,
    has_remote,
    is_clean,
    load_state,
    main_checkout,
    worktrees,
)

GRAPH_ENV = "SWARM_TICKET_GRAPH"
GRAPH = Path("docs/specs/roadmap/gantt/ticket-graph.json")
WORKSPACE = "swarm.code-workspace"
HOOKS_PATH = ".githooks"
TICKET_ID = re.compile(r"^T\d+\.\d{2}$")
EXTENSIONS = [
    "anthropic.claude-code",
    "GitHub.vscode-pull-request-github",
    "eamodio.gitlens",
    "mhutchie.git-graph",
    "ms-python.python",
    "charliermarsh.ruff",
    "rust-lang.rust-analyzer",
    "bierner.markdown-mermaid",
]
WORKSPACE_SETTINGS = {
    "scm.alwaysShowRepositories": True,
    "scm.repositories.visible": 12,
    "git.autoRepositoryDetection": True,
    "git.openRepositoryInParentFolders": "always",
    "githubPullRequests.defaultMergeMethod": "merge",
    "gitlens.views.worktrees.files.layout": "tree",
}
GIT_CONFIG = {"core.hooksPath": HOOKS_PATH, "push.autoSetupRemote": "true", "fetch.prune": "true"}
STATE_ICONS = {"planned": "📝", "running": "🔄", "integrated": "🧩", "committed": "📦", "merged": "🏁"}


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


def open_tickets(main: Path) -> Dict[str, Path]:
    """Return every open ticket with its worktree: the checkouts on a ``feature/<ID>`` branch."""
    found: Dict[str, Path] = {}
    for path, branch in worktrees(main):
        ticket = branch[len(BRANCH_PREFIX) :] if branch.startswith(BRANCH_PREFIX) else ""
        if TICKET_ID.match(ticket):
            found[ticket] = path
    return dict(sorted(found.items(), key=lambda item: key(item[0])))


def title_of(home: Path, ticket: str) -> str:
    path = home / "docs" / "tickets" / ticket / "TICKET.md"
    if path.is_file():
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.startswith("# "):
                return line[2:].split(":", 1)[-1].strip()
    return ""


def problems(main: Path, ticket: str) -> List[str]:
    """Return why a ticket may not start yet (TKT-16), one sentence each."""
    tickets = graph(main)
    if ticket not in tickets:
        return [f"{ticket} is not in the ticket graph: add it to {GRAPH} first."]
    info = tickets[ticket]
    ref = develop_ref(main, fetch=True)
    done = merged_tickets(main, ref)
    found: List[str] = []
    waiting = [dep for dep in info.get("deps", []) if dep not in done]  # type: ignore[union-attr]
    if waiting:
        found.append(
            f"{', '.join(waiting)} not merged on {ref} yet: {ticket} builds on {'it' if len(waiting) == 1 else 'them'}."
        )
    field = info.get("field")
    if isinstance(field, dict):
        found.append(
            f"{ticket} fixes what {field.get('after')} finds: it starts once that has flown ({field.get('start')})."
        )
    mine = areas(str(info.get("area", "")))
    for other, home in open_tickets(main).items():
        if other == ticket:
            continue
        theirs = areas(str(tickets.get(other, {}).get("area", "")))
        shared = sorted((mine & theirs) or (mine | theirs if "*" in mine or "*" in theirs else set()))
        if shared:
            found.append(f"{other} is open in {home} and changes {', '.join(shared)}: wait for its merge (area lock).")
    return found


def state_of(main: Path, home: Path, ticket: str, done: Set[str]) -> Tuple[str, str]:
    """Return the state of an open ticket and a detail for the list."""
    if ticket in done:
        return "merged", "on develop, run prune"
    state = load_state(home, ticket)
    integrated = state.get("integrated") or []
    count = len(integrated) if isinstance(integrated, list) else 0
    ahead = git(home, "rev-list", "--count", f"{DEVELOP}..HEAD", check=False)[1] or "0"
    if ahead != "0":
        return "committed", "pull request open or to open"
    if count:
        return "integrated", f"{count} task(s) integrated"
    plan = home / "docs" / "tickets" / ticket / "PLAN.md"
    if plan.is_file() and "🟢 Approved" in plan.read_text(encoding="utf-8"):
        return "running", "plan approved"
    return "planned", "plan awaits approval"


def remote_detail(home: Path, ticket: str) -> str:
    result = subprocess.run(
        [
            "gh",
            "pr",
            "view",
            f"{BRANCH_PREFIX}{ticket}",
            "--json",
            "number,statusCheckRollup,state",
            "--jq",
            '"#\\(.number) \\(.state) " + ([.statusCheckRollup[]?.conclusion // "PENDING"] | unique | join(","))',
        ],
        cwd=home,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else "no pull request"


def show_list(main: Path, remote: bool) -> None:
    tickets = open_tickets(main)
    if not tickets:
        print("No open ticket. Start one with /ticket-plan <ID>, then /ticket-run <ID>.")
        return
    done = merged_tickets(main, develop_ref(main))
    graph_tickets = graph(main)
    print(f"🎫 {len(tickets)} open ticket(s)")
    for ticket, home in tickets.items():
        state, detail = state_of(main, home, ticket, done)
        area = ", ".join(sorted(areas(str(graph_tickets.get(ticket, {}).get("area", "")))))
        extra = f" · {remote_detail(home, ticket)}" if remote else ""
        print(f"  {STATE_ICONS[state]} {ticket}  {title_of(home, ticket)[:60]}")
        print(f"       {detail}{extra} · 🗂️ {area} · 📁 {home}")


def write_workspace(main: Path) -> Path:
    folders: List[Dict[str, str]] = [{"path": ".", "name": "🏠 develop (main checkout)"}]
    for ticket, home in open_tickets(main).items():
        folders.append({"path": str(home), "name": f"🎫 {ticket} · {title_of(home, ticket)[:50]}".rstrip(" ·")})
    path = main / WORKSPACE
    content = {"folders": folders, "settings": WORKSPACE_SETTINGS, "extensions": {"recommendations": EXTENSIONS}}
    path.write_text(json.dumps(content, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def prune(main: Path) -> List[str]:
    """Remove the worktrees and local branches of the merged tickets, and bring develop up to date."""
    ref = develop_ref(main, fetch=True)
    done = merged_tickets(main, ref)
    removed: List[str] = []
    for ticket, home in open_tickets(main).items():
        branch = f"{BRANCH_PREFIX}{ticket}"
        if ticket not in done or git(main, "merge-base", "--is-ancestor", branch, ref, check=False)[0] != 0:
            continue
        if not is_clean(home):
            print(f"⚠️  {ticket} is merged but {home} has changes: kept.")
            continue
        git(main, "worktree", "remove", "--force", str(home))
        git(main, "branch", "-D", branch, check=False)
        removed.append(ticket)
        print(f"🧹 {ticket}: worktree and branch removed")
    on_develop = git(main, "branch", "--show-current")[1] == DEVELOP
    if (
        ref != DEVELOP
        and on_develop
        and is_clean(main)
        and git(main, "merge", "--ff-only", "--quiet", ref, check=False)[0] == 0
    ):
        print(f"⏩ develop fast-forwarded to {ref}")
    write_workspace(main)
    return removed


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
    listing = sub.add_parser("list")
    listing.add_argument("--remote", action="store_true")
    for name in ("prune", "workspace", "setup"):
        sub.add_parser(name)
    args = parser.parse_args(argv)
    top = Path(git(Path.cwd(), "rev-parse", "--show-toplevel")[1])
    main_dir = main_checkout(top)
    if args.command == "check":
        found = problems(main_dir, args.ticket)
        for problem in found:
            print(problem)
        return 1 if found and not args.force else 0
    if args.command == "list":
        show_list(main_dir, args.remote)
    elif args.command == "prune":
        prune(main_dir)
    elif args.command == "workspace":
        print(write_workspace(main_dir))
    else:
        setup(main_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
