from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List

from pydantic import JsonValue

TICKET = "T9.01"
OTHER = "T9.02"
SHARED_BRANCH = "feature/tickets"
LEGACY_BRANCH = f"ticket/{TICKET}"
TICKET_FOLDER = f"docs/tickets/{TICKET}"
TICKET_TITLE = f"{TICKET}: Smoke ticket"
CHANGES_MARKERS = "<!-- changes -->\n<!-- /changes -->\n"
GIT_ENV: Dict[str, str] = {
    "GIT_AUTHOR_NAME": "Test",
    "GIT_AUTHOR_EMAIL": "test@example.com",
    "GIT_COMMITTER_NAME": "Test",
    "GIT_COMMITTER_EMAIL": "test@example.com",
}
INTEGRATED_KEY = "integrated"
CONFLICTS_KEY = "conflicts"
REMAINING_KEY = "remaining"
TREE_KEY = "tree"
FILES_KEY = "files"
COMMIT_KEY = "commit"
MERGE_KEY = "merge"
HOME_KEY = "home"
PUSHED_KEY = "pushed"


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def script_path() -> Path:
    return repo_root() / ".claude" / "scripts" / "ticket_tree.py"


def environment() -> Dict[str, str]:
    return {**os.environ, **GIT_ENV}


def git(cwd: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=cwd, check=True, capture_output=True, text=True, encoding="utf-8", env=environment()
    )
    return result.stdout.strip()


def run(cwd: Path, *args: str, ticket: str = TICKET) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script_path()), *args, "--ticket", ticket],
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=environment(),
        timeout=120,
    )


def run_json(cwd: Path, *args: str) -> Dict[str, JsonValue]:
    result = run(cwd, *args)
    assert result.returncode == 0, result.stderr
    loaded: Dict[str, JsonValue] = json.loads(result.stdout)
    return loaded


def legacy_home(main: Path) -> Path:
    """Return where a ticket started before TKT-16 kept its own worktree, beside the main checkout."""
    return main.parent / f"{main.name}-tickets" / TICKET


def add_ticket(main: Path, ticket: str) -> None:
    """Write a second ticket's folder, uncommitted, as /ticket-plan does."""
    folder = main / "docs" / "tickets" / ticket
    folder.mkdir(parents=True)
    (folder / "TICKET.md").write_text(f"# {ticket}: Second ticket\n", encoding="utf-8")
    (folder / "EXPLAIN.md").write_text(f"# Explain\n\n\n\n{CHANGES_MARKERS}", encoding="utf-8")
    (folder / "IMPLEMENTATION.md").write_text("# Implementation\n\n\n", encoding="utf-8")


def make_repo(base: Path) -> Path:
    """Create a repository on ``develop`` with one commit and an uncommitted ticket folder, and return its path."""
    main = base / "main"
    main.mkdir()
    git(main, "init", "-b", "develop")
    (main / "a.txt").write_text("a\nb\nc\n", encoding="utf-8")
    git(main, "add", "-A")
    git(main, "commit", "-m", "initial")
    folder = main / TICKET_FOLDER
    folder.mkdir(parents=True)
    (folder / "TICKET.md").write_text(f"# {TICKET_TITLE}\n", encoding="utf-8")
    write_documents(main, "", "")
    return main


def write_documents(checkout: Path, explain: str, implementation: str) -> None:
    """Write ``EXPLAIN.md`` (around the empty changes markers) and ``IMPLEMENTATION.md`` of the ticket."""
    folder = checkout / TICKET_FOLDER
    (folder / "EXPLAIN.md").write_text(f"# Explain\n\n{explain}\n\n{CHANGES_MARKERS}", encoding="utf-8")
    (folder / "IMPLEMENTATION.md").write_text(f"# Implementation\n\n{implementation}\n", encoding="utf-8")


def integrated_repo(base: Path) -> Path:
    """Create a repository whose ticket integrated one task changing ``a.txt`` (lines 2 and 4 of 4)."""
    main = make_repo(base)
    assert run(main, "prepare").returncode == 0
    worker_writes(main, "w1", "K01", {"a.txt": "a\nB\nc\nd\n"})
    assert run(main, "integrate", "--task", "K01").returncode == 0
    return main


def documents_problems(main: Path, explain: str, implementation: str) -> str:
    """Write the documents, generate their changes table, and return what ``docs`` prints."""
    write_documents(main, explain, implementation)
    assert run(main, "changes", "--write").returncode == 0
    return run(main, "docs").stdout


def add_worktree(main: Path, name: str, start: str = "HEAD") -> Path:
    """Add a worker worktree from the main checkout, as Claude Code does for an agent of the workflow."""
    path = main.parent / name
    git(main, "worktree", "add", "-b", f"worktree-{name}", str(path), start)
    return path


def commit_count(main: Path, branch: str) -> int:
    return int(git(main, "rev-list", "--count", branch))


def worker_writes(main: Path, name: str, task: str, files: Dict[str, str], ticket: str = TICKET) -> Path:
    """Start a worker worktree, write ``files`` into it and hand them off as ``task`` of ``ticket``."""
    worker = add_worktree(main, name)
    assert run(worker, "start", ticket=ticket).returncode == 0
    for relative, text in files.items():
        path = worker / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    assert run(worker, "handoff", "--task", task, ticket=ticket).returncode == 0
    return worker


def task_args(tasks: List[str]) -> List[str]:
    args: List[str] = []
    for task in tasks:
        args.extend(["--task", task])
    return args
