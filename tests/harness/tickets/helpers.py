from __future__ import annotations

# Standard library imports
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

GIT_ENV: Dict[str, str] = {
    "GIT_AUTHOR_NAME": "Test",
    "GIT_AUTHOR_EMAIL": "test@example.com",
    "GIT_COMMITTER_NAME": "Test",
    "GIT_COMMITTER_EMAIL": "test@example.com",
}
GRAPH_ENV = "SWARM_TICKET_GRAPH"
CHECK_PLAN_ENV = "SWARM_CHECK_PLAN"
CLOSED_ENV = "SWARM_CLOSED_ISSUES"
SHARED_BRANCH = "feature/tickets"
DONE = "T9.00"
NEXT = "T9.01"
SAME_AREA = "T9.02"
OTHER_AREA = "T9.03"
FIELD = "T9.04"
GRAPH: Dict[str, Dict[str, Dict[str, object]]] = {
    "tickets": {
        DONE: {"deps": [], "external": [], "area": "backend/apps/missions", "size": "S"},
        NEXT: {"deps": [DONE], "external": [], "area": "backend/apps/missions", "size": "M"},
        SAME_AREA: {
            "deps": [],
            "external": [],
            "area": "backend/apps/missions, frontend/apps/back-office",
            "size": "M",
        },
        OTHER_AREA: {"deps": [NEXT], "external": [], "area": "rust", "size": "L"},
        FIELD: {
            "deps": [],
            "external": ["C-01"],
            "area": "tests/flight",
            "size": "S",
            "field": {"after": "C-01", "start": "2027-05-10", "end": "2027-06-18"},
        },
    }
}
PHASE = "P9"
EPIC = "E9.1"
ISSUES: Dict[str, int] = {PHASE: 1, EPIC: 2, DONE: 3, NEXT: 4, SAME_AREA: 5, OTHER_AREA: 6, FIELD: 7}
GITHUB_STATE: Dict[str, object] = {
    "issues": {ident: {"number": number} for ident, number in ISSUES.items()},
    "subissues": [[PHASE, EPIC], [EPIC, DONE], [EPIC, NEXT], [EPIC, OTHER_AREA], [PHASE, SAME_AREA]],
}
AWAITING = "**Plan:** 🟡 Awaiting approval"
APPROVED = "**Plan:** 🟢 Approved"
TASK_ID_KEY = "id"
TASK_FILES_KEY = "files"
TICKET_KEY = "ticket"
INTEGRATED_KEY = "integrated"
PATHS_KEY = "paths"
HOME_KEY = "home"
TICKETS_KEY = "tickets"
DEPS_KEY = "deps"
EXTERNAL_KEY = "external"
AREA_KEY = "area"
SIZE_KEY = "size"


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def environment(graph: Path, check_plan: str = "true", closed: str = "") -> Dict[str, str]:
    return {**os.environ, **GIT_ENV, GRAPH_ENV: str(graph), CHECK_PLAN_ENV: check_plan, CLOSED_ENV: closed}


def git(cwd: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=cwd, check=True, capture_output=True, text=True, env={**os.environ, **GIT_ENV}
    )
    return result.stdout.strip()


def make_repo(base: Path) -> Path:
    """Create a repository on ``develop`` where DONE is merged (its EXPLAIN.md is committed), the graph and github.json."""
    main = base / "main"
    (main / "docs" / "tickets" / DONE).mkdir(parents=True)
    git(main, "init", "-b", "develop")
    (main / "docs" / "tickets" / DONE / "EXPLAIN.md").write_text("# Explain\n", encoding="utf-8")
    git(main, "add", "-A")
    git(main, "commit", "-m", f"{DONE}: done")
    (main / ".claude").mkdir()
    (main / ".claude" / "github.json").write_text(json.dumps(GITHUB_STATE), encoding="utf-8")
    (base / "graph.json").write_text(json.dumps(GRAPH), encoding="utf-8")
    return main


def open_ticket(
    main: Path, ticket: str, paths: Optional[List[str]] = None, integrated: Optional[List[str]] = None
) -> None:
    """Record a running ticket in the shared checkout, as ticket_tree.py prepare does, with its integrated tasks."""
    state = main / ".git" / "swarm" / ticket
    state.mkdir(parents=True)
    content = {
        TICKET_KEY: ticket,
        INTEGRATED_KEY: integrated or [],
        PATHS_KEY: paths or [f"docs/tickets/{ticket}/"],
        HOME_KEY: str(main),
    }
    (state / "state.json").write_text(json.dumps(content), encoding="utf-8")


def legacy_ticket(main: Path, ticket: str) -> Path:
    """Give a ticket its own worktree, as before TKT-16 shared the checkout, and return it."""
    home = main.parent / "main-tickets" / ticket
    git(main, "worktree", "add", "-b", f"feature/{ticket}", str(home), "develop")
    return home


def write_plan(main: Path, ticket: str, status: str) -> Path:
    folder = main / "docs" / "tickets" / ticket
    folder.mkdir(parents=True, exist_ok=True)
    plan = folder / "PLAN.md"
    plan.write_text(f"# {ticket}: Plan\n\n{status}\n\nTasks.\n", encoding="utf-8")
    (folder / "PROGRESS.md").write_text(
        f"# {ticket}: Progress\n\n## 📝 Events\n\n| Time | Event | By | Result |\n| --- | --- | --- | --- |\n",
        encoding="utf-8",
    )
    return plan


def write_plan_with_tasks(main: Path, ticket: str, status: str, tasks: List[Tuple[str, List[str]]]) -> Path:
    """Write a plan whose json block holds ``tasks``, each an id with the files it owns."""
    plan = write_plan(main, ticket, status)
    graph = [{TASK_ID_KEY: task_id, TASK_FILES_KEY: files} for task_id, files in tasks]
    plan.write_text(
        f"{plan.read_text(encoding='utf-8')}\n```json\n{json.dumps(graph, indent=2)}\n```\n", encoding="utf-8"
    )
    return plan


def add_ticket_to_graph(main: Path, ticket: str, area: str) -> None:
    """Add a ticket without prerequisites to the ticket graph of the repository made by ``make_repo``."""
    path = main.parent / "graph.json"
    loaded = json.loads(path.read_text(encoding="utf-8"))
    loaded[TICKETS_KEY][ticket] = {DEPS_KEY: [], EXTERNAL_KEY: [], AREA_KEY: area, SIZE_KEY: "S"}
    path.write_text(json.dumps(loaded), encoding="utf-8")


def run(main: Path, *args: str, check_plan: str = "true", closed: str = "") -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(repo_root() / ".claude" / "scripts" / "tickets" / "tickets.py"), *args],
        cwd=main,
        check=False,
        capture_output=True,
        text=True,
        env=environment(main.parent / "graph.json", check_plan, closed),
        timeout=60,
    )


def finish_on_shared_branch(main: Path, ticket: str) -> None:
    """Commit a finished ticket on feature/tickets, its pull request still open."""
    git(main, "checkout", "-B", SHARED_BRANCH)
    git(main, "commit", "--allow-empty", "-m", f"{ticket}: finished, pull request open")


def lines(result: subprocess.CompletedProcess[str]) -> List[str]:
    return [line for line in result.stdout.splitlines() if line.strip()]


def branch_with_commit(main: Path, branch: str, name: str, content: str, message: str) -> str:
    """Create ``branch`` from ``develop`` with one commit writing ``name``, come back to ``develop``, return the commit."""
    git(main, "checkout", "-q", "-b", branch, "develop")
    (main / name).write_text(content, encoding="utf-8")
    git(main, "add", name)
    git(main, "commit", "-q", "-m", message)
    commit = git(main, "rev-parse", "HEAD")
    git(main, "checkout", "-q", "develop")
    return commit


def add_remote(main: Path, *branches: str) -> Path:
    """Give the repository a bare ``origin`` holding ``develop``, ``master`` and ``branches``, and return it."""
    remote = main.parent / "origin.git"
    git(main.parent, "init", "-q", "--bare", str(remote))
    git(main, "remote", "add", "origin", str(remote))
    git(main, "branch", "-f", "master", "develop")
    git(main, "push", "-q", "origin", "develop", "master", *branches)
    git(main, "fetch", "-q", "origin")
    return remote
