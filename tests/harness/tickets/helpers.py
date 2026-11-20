from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional

GIT_ENV: Dict[str, str] = {
    "GIT_AUTHOR_NAME": "Test",
    "GIT_AUTHOR_EMAIL": "test@example.com",
    "GIT_COMMITTER_NAME": "Test",
    "GIT_COMMITTER_EMAIL": "test@example.com",
}
GRAPH_ENV = "SWARM_TICKET_GRAPH"
CHECK_PLAN_ENV = "SWARM_CHECK_PLAN"
SHARED_BRANCH = "feature/tickets"
DONE = "T9.00"
NEXT = "T9.01"
SAME_AREA = "T9.02"
OTHER_AREA = "T9.03"
FIELD = "T9.04"
GRAPH: Dict[str, Dict[str, Dict[str, object]]] = {
    "tickets": {
        DONE: {"deps": [], "external": [], "area": "services/missions", "size": "S"},
        NEXT: {"deps": [DONE], "external": [], "area": "services/missions", "size": "M"},
        SAME_AREA: {"deps": [], "external": [], "area": "services/missions, frontends/back-office", "size": "M"},
        OTHER_AREA: {"deps": [NEXT], "external": [], "area": "packages/rust", "size": "L"},
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


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def environment(graph: Path, check_plan: str = "true") -> Dict[str, str]:
    return {**os.environ, **GIT_ENV, GRAPH_ENV: str(graph), CHECK_PLAN_ENV: check_plan}


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


def open_ticket(main: Path, ticket: str, paths: Optional[List[str]] = None) -> None:
    """Record a running ticket in the shared checkout, as ticket_tree.py prepare does."""
    state = main / ".git" / "swarm" / ticket
    state.mkdir(parents=True)
    content = {"ticket": ticket, "integrated": [], "paths": paths or [f"docs/tickets/{ticket}/"], "home": str(main)}
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


def run(main: Path, *args: str, check_plan: str = "true") -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(repo_root() / ".claude" / "scripts" / "tickets.py"), *args],
        cwd=main,
        check=False,
        capture_output=True,
        text=True,
        env=environment(main.parent / "graph.json", check_plan),
        timeout=60,
    )


def lines(result: subprocess.CompletedProcess[str]) -> List[str]:
    return [line for line in result.stdout.splitlines() if line.strip()]
