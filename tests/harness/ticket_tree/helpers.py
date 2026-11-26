from __future__ import annotations

# Standard library imports
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Third-party imports
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
REFUSED_KEY = "refused"
PULL_REQUEST_KEY = "pull_request"
PULL_REQUEST_ERROR_KEY = "pull_request_error"
PATH_KEY = "PATH"
GH_LOG_KEY = "FAKE_GH_LOG"
GH_OPEN_KEY = "FAKE_GH_OPEN"
GH_API_FAILS_KEY = "FAKE_GH_API_FAILS"
OPEN_PULL_REQUEST = "https://example.com/pull/7"
# A stand-in for gh: it logs every call, fails ``pr edit`` as GitHub does since Projects (classic) is deprecated (L-30,
# L-36), lists one open pull request when FAKE_GH_OPEN is set, and fails ``gh api`` when FAKE_GH_API_FAILS is set.
FAKE_GH = f"""#!{sys.executable}
import json, os, sys
args = sys.argv[1:]
with open(os.environ["{GH_LOG_KEY}"], "a", encoding="utf-8") as log:
    log.write(json.dumps(args) + "\\n")
if args[:2] == ["pr", "edit"]:
    print("GraphQL: Projects (classic) is being deprecated", file=sys.stderr)
    sys.exit(1)
if args[:2] == ["pr", "list"]:
    print(json.dumps([{{"number": 7, "url": "{OPEN_PULL_REQUEST}"}}] if os.environ.get("{GH_OPEN_KEY}") else []))
    sys.exit(0)
if args[:1] == ["api"] and os.environ.get("{GH_API_FAILS_KEY}"):
    print("HTTP 502: Bad Gateway", file=sys.stderr)
    sys.exit(1)
if args[:2] == ["pr", "create"]:
    print("https://example.com/pull/8")
sys.exit(0)
"""


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def script_path() -> Path:
    return repo_root() / ".claude" / "scripts" / "tickets" / "ticket_tree.py"


def environment() -> Dict[str, str]:
    return {**os.environ, **GIT_ENV}


def git(cwd: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=cwd, check=True, capture_output=True, text=True, encoding="utf-8", env=environment()
    )
    return result.stdout.strip()


def run(
    cwd: Path, *args: str, ticket: str = TICKET, env: Optional[Dict[str, str]] = None
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script_path()), *args, "--ticket", ticket],
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env if env else environment(),
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


def fake_gh(folder: Path, open_pull_request: bool, api_fails: bool) -> Dict[str, str]:
    """Install the stand-in ``gh`` in ``folder`` and return the environment that puts it first on the PATH."""
    folder.mkdir(parents=True, exist_ok=True)
    script = folder / "gh"
    script.write_text(FAKE_GH, encoding="utf-8")
    script.chmod(0o755)
    env = {**environment(), PATH_KEY: f"{folder}{os.pathsep}{os.environ[PATH_KEY]}", GH_LOG_KEY: str(folder / "log")}
    if open_pull_request:
        env[GH_OPEN_KEY] = "1"
    if api_fails:
        env[GH_API_FAILS_KEY] = "1"
    return env


def gh_calls(folder: Path) -> List[List[str]]:
    """Return every call the stand-in ``gh`` received, oldest first."""
    log = folder / "log"
    if not log.is_file():
        return []
    return [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines() if line]
