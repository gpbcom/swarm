from __future__ import annotations

# Standard library imports
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict

GIT_ENV: Dict[str, str] = {
    "GIT_AUTHOR_NAME": "Test",
    "GIT_AUTHOR_EMAIL": "test@example.com",
    "GIT_COMMITTER_NAME": "Test",
    "GIT_COMMITTER_EMAIL": "test@example.com",
}
BYPASS_ENV = "SWARM_GITFLOW_BYPASS"


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def environment(**extra: str) -> Dict[str, str]:
    clean = {k: v for k, v in os.environ.items() if k != BYPASS_ENV}
    return {**clean, **GIT_ENV, **extra}


def git(cwd: Path, *args: str, **extra: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args], cwd=cwd, capture_output=True, text=True, check=False, env=environment(**extra)
    )


def make_repo(base: Path) -> Path:
    """Create a repository on ``develop`` with the hooks of this repository turned on."""
    main = base / "main"
    main.mkdir()
    git(main, "init", "-b", "develop")
    git(main, "commit", "--allow-empty", "-m", "initial", "--no-verify")
    hooks = repo_root() / ".githooks"
    git(main, "config", "core.hooksPath", str(hooks))
    return main


def commit(main: Path, message: str, **extra: str) -> subprocess.CompletedProcess[str]:
    (main / "file.txt").write_text(message + "\n", encoding="utf-8")
    git(main, "add", "file.txt")
    return git(main, "commit", "-m", message, **extra)


def guard(command: str, cwd: Path) -> Dict[str, object]:
    """Run the PreToolUse hook on a Bash command and return its decision (empty when it lets it run)."""
    payload = {
        "hook_event_name": "PreToolUse",
        "tool_name": "Bash",
        "tool_input": {"command": command},
        "cwd": str(cwd),
    }
    result = subprocess.run(
        [sys.executable, str(repo_root() / ".claude" / "hooks" / "guard_git.py")],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        check=False,
        env=environment(),
    )
    assert result.returncode == 0, result.stderr
    if not result.stdout.strip():
        return {}
    decision: Dict[str, object] = json.loads(result.stdout)["hookSpecificOutput"]
    return decision
