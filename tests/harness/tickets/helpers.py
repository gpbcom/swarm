from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List

GIT_ENV: Dict[str, str] = {
    "GIT_AUTHOR_NAME": "Test",
    "GIT_AUTHOR_EMAIL": "test@example.com",
    "GIT_COMMITTER_NAME": "Test",
    "GIT_COMMITTER_EMAIL": "test@example.com",
}
GRAPH_ENV = "SWARM_TICKET_GRAPH"
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


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def environment(graph: Path) -> Dict[str, str]:
    return {**os.environ, **GIT_ENV, GRAPH_ENV: str(graph)}


def git(cwd: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=cwd, check=True, capture_output=True, text=True, env={**os.environ, **GIT_ENV}
    )
    return result.stdout.strip()


def make_repo(base: Path) -> Path:
    """Create a repository on ``develop`` where DONE is merged (its EXPLAIN.md is committed), and the graph."""
    main = base / "main"
    (main / "docs" / "tickets" / DONE).mkdir(parents=True)
    git(main, "init", "-b", "develop")
    (main / "docs" / "tickets" / DONE / "EXPLAIN.md").write_text("# Explain\n", encoding="utf-8")
    git(main, "add", "-A")
    git(main, "commit", "-m", f"{DONE}: done")
    (base / "graph.json").write_text(json.dumps(GRAPH), encoding="utf-8")
    return main


def open_ticket(main: Path, ticket: str) -> Path:
    """Give a ticket its worktree, as ticket_tree.py prepare does, and return it."""
    home = main.parent / "main-tickets" / ticket
    git(main, "worktree", "add", "-b", f"feature/{ticket}", str(home), "develop")
    return home


def run(main: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(repo_root() / ".claude" / "scripts" / "tickets.py"), *args],
        cwd=main,
        check=False,
        capture_output=True,
        text=True,
        env=environment(main.parent / "graph.json"),
        timeout=60,
    )


def lines(result: subprocess.CompletedProcess[str]) -> List[str]:
    return [line for line in result.stdout.splitlines() if line.strip()]
