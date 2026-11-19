from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional

GIT_IDENTITY = ["-c", "user.name=Test", "-c", "user.email=test@example.com"]
COUNTER_NAME = "swarm-check-touched-blocks"
FAIL_CODE = (
    "import sys, pathlib\n"
    "bad = [f for f in sys.argv[1:] if 'FAIL' in pathlib.Path(f).read_text()]\n"
    "sys.exit(1 if bad else 0)"
)


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def script_path() -> Path:
    return repo_root() / ".claude" / "hooks" / "check_touched.py"


def git(cwd: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *GIT_IDENTITY, *args], cwd=cwd, check=True, capture_output=True, text=True, encoding="utf-8"
    )
    return result.stdout.strip()


def catalogue_text(rules: List[Dict[str, object]], max_blocks: int = 2) -> str:
    return json.dumps({"max_blocks": max_blocks, "rules": rules})


def failing_rule() -> Dict[str, object]:
    return {"name": "no-fail", "match": r"\.txt$", "run": [sys.executable, "-c", FAIL_CODE, "{files}"]}


def echo_rule() -> Dict[str, object]:
    return {"name": "seen", "match": r"\.txt$", "run": ["echo", "{files}"]}


def make_repo(base: Path, catalogue: Optional[str]) -> Path:
    """Create a repository on ``develop`` with one commit, and return its path."""
    main = base / "main"
    main.mkdir()
    git(main, "init", "-b", "develop")
    (main / "old.txt").write_text("old\n", encoding="utf-8")
    if catalogue is not None:
        hooks = main / ".claude" / "hooks"
        hooks.mkdir(parents=True)
        (hooks / "layer-checks.json").write_text(catalogue, encoding="utf-8")
    git(main, "add", "-A")
    git(main, "commit", "-m", "initial")
    return main


def add_worktree(main: Path, base: Path) -> Path:
    path = base / "worker"
    git(main, "worktree", "add", "-b", "task", str(path), "develop")
    return path


def git_dir(cwd: Path) -> Path:
    return Path(git(cwd, "rev-parse", "--absolute-git-dir"))


def run_hook(cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
    payload = json.dumps({"cwd": str(cwd), "hook_event_name": "SubagentStop"})
    return subprocess.run(
        [sys.executable, str(script_path()), *args],
        cwd=cwd,
        check=False,
        input=payload,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=120,
    )
