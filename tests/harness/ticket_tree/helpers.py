from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List

from pydantic import JsonValue

TICKET = "T9.01"
TICKET_BRANCH = f"ticket/{TICKET}"
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


def run(cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script_path()), *args, "--ticket", TICKET],
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
    (folder / "EXPLAIN.md").write_text(f"# Explain\n\n{CHANGES_MARKERS}", encoding="utf-8")
    return main


def add_worktree(main: Path, name: str) -> Path:
    path = main.parent / name
    git(main, "worktree", "add", "-b", f"worktree-{name}", str(path), "HEAD")
    return path


def commit_count(main: Path, branch: str) -> int:
    return int(git(main, "rev-list", "--count", branch))


def worker_writes(main: Path, name: str, task: str, files: Dict[str, str]) -> Path:
    """Start a worker worktree, write ``files`` into it and hand them off as ``task``."""
    worker = add_worktree(main, name)
    assert run(worker, "start").returncode == 0
    for relative, text in files.items():
        path = worker / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    assert run(worker, "handoff", "--task", task).returncode == 0
    return worker


def task_args(tasks: List[str]) -> List[str]:
    args: List[str] = []
    for task in tasks:
        args.extend(["--task", task])
    return args
