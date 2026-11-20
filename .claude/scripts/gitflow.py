#!/usr/bin/env python3
from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

USAGE = """The GitFlow rules of Swarm, run by the git hooks of ``.githooks/`` (TKT-15).

Usage (by git, through ``.githooks/``; turned on per clone by ``python3 .claude/scripts/tickets.py setup``):
    gitflow.py pre-commit
    gitflow.py commit-msg <message file>
    gitflow.py pre-push <remote> <url>          (the refs pushed come on stdin)

- ``develop`` and ``master`` change only through pull requests: no commit on them, no push to them, and they are never
  deleted on the remote (TKT-25).
- Branches follow GitFlow: ``feature/<name>`` (a ticket is ``feature/<ID>``), ``release/<version>``,
  ``hotfix/<name>``, ``bugfix/<name>``, ``support/<name>``. The workers' ``worktree-*`` branches never commit (TKT-5).
- A commit on a ticket's branch, or on the tickets' shared branch ``feature/tickets``, starts with a ticket ID:
  ``T0.09: NATS JetStream and Operator accounts``.

``SWARM_GITFLOW_BYPASS=1`` lets the person step outside these rules on purpose (a first push, a release tag).
Each refusal prints its reason and the way out on stderr, and exits 1.
"""

BYPASS_ENV = "SWARM_GITFLOW_BYPASS"
PROTECTED = ("develop", "master", "main")
GITFLOW = re.compile(r"^(feature|bugfix|hotfix|support)/[A-Za-z0-9._-]+$|^release/v?\d+\.\d+(\.\d+)?$")
WORKER = re.compile(r"^worktree-")
LEGACY = re.compile(r"^ticket/T\d+\.\d{2}$")
TICKET_BRANCH = re.compile(r"^feature/(T\d+\.\d{2})$")
SHARED_BRANCH = "feature/tickets"
ANY_TICKET = re.compile(r"^T\d+\.\d{2}[: ]")
ZERO = "0" * 40


def branch() -> str:
    result = subprocess.run(["git", "branch", "--show-current"], capture_output=True, text=True, check=False)
    return result.stdout.strip()


def refuse(reason: str, way_out: str) -> int:
    print(f"⛔ GitFlow (TKT-15): {reason}\n   ➜ {way_out}", file=sys.stderr)
    return 1


def bypassed() -> bool:
    return os.environ.get(BYPASS_ENV) == "1"


def name_problem(name: str) -> Optional[str]:
    """Return why a branch name breaks GitFlow, or None."""
    if name in PROTECTED or GITFLOW.match(name) or LEGACY.match(name) or WORKER.match(name) or not name:
        return None
    return f"the branch {name!r} is not a GitFlow branch."


def pre_commit() -> int:
    if bypassed():
        return 0
    current = branch()
    if current in PROTECTED:
        return refuse(
            f"no commit on {current}: it changes through pull requests.",
            "git switch -c feature/<name>, commit there, push it and open a pull request "
            "(a ticket: /ticket-run <ID> does all of it).",
        )
    if WORKER.match(current):
        return refuse(
            "a worker never commits (TKT-5): its work is handed off uncommitted.",
            "python3 .claude/scripts/ticket_tree.py handoff --ticket <ID> --task <K..>",
        )
    problem = name_problem(current)
    if problem:
        return refuse(problem, "use feature/<name>, release/<version>, hotfix/<name>, bugfix/<name> or support/<name>.")
    return 0


def commit_msg(path: str) -> int:
    if bypassed():
        return 0
    subject = next((line for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()), "")
    if subject.startswith(("Merge ", "Revert ", "fixup! ", "squash! ")):
        return 0
    if branch() == SHARED_BRANCH and not ANY_TICKET.match(subject):
        return refuse(
            f"a commit on {SHARED_BRANCH} is one ticket's commit and starts with its ID.",
            '"T0.10: <title of TICKET.md>" (python3 .claude/scripts/ticket_tree.py finish writes it).',
        )
    ticket = TICKET_BRANCH.match(branch())
    if ticket and not re.match(rf"^{re.escape(ticket.group(1))}[: ]", subject):
        return refuse(
            f"a commit of ticket {ticket.group(1)} starts with its ID.",
            f'"{ticket.group(1)}: <title of TICKET.md>"',
        )
    return 0


def pre_push(lines: List[str]) -> int:
    if bypassed():
        return 0
    for line in lines:
        parts = line.split()
        if len(parts) != 4:
            continue
        target = parts[2].removeprefix("refs/heads/")
        if parts[1] == ZERO:
            if target in PROTECTED:
                return refuse(
                    f"{target} is never deleted (TKT-25).",
                    "delete only branches whose work develop holds: python3 .claude/scripts/tickets.py prune.",
                )
            continue
        if target in PROTECTED:
            return refuse(
                f"no push to {target}: it changes through pull requests.",
                f"push a feature/, release/ or hotfix/ branch and open a pull request to {target}.",
            )
        problem = name_problem(target)
        if problem or WORKER.match(target):
            return refuse(problem or "worker branches stay local (TKT-5).", "push only GitFlow branches.")
    return 0


def main(argv: List[str]) -> int:
    if not argv:
        print(USAGE, file=sys.stderr)
        return 2
    if argv[0] == "pre-commit":
        return pre_commit()
    if argv[0] == "commit-msg":
        return commit_msg(argv[1])
    if argv[0] == "pre-push":
        return pre_push(sys.stdin.read().splitlines())
    print(f"Unknown hook {argv[0]!r}.", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
