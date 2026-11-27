from __future__ import annotations

# Standard library imports
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional

REPOSITORY = Path(__file__).resolve().parents[3]
SCRIPT = REPOSITORY / ".claude" / "scripts" / "reports" / "progress.py"
RUN_ID = "wf_config_dir_probe"
LABEL = "config-dir-probe"
HOME_KEY = "HOME"
CONFIG_KEY = "CLAUDE_CONFIG_DIR"
STARTED = {"type": "started", "key": "k1", "label": LABEL, "phase": "Probe", "agentId": "a1"}
NOT_FOUND = "No workflow found"


def main_checkout() -> Path:
    out = subprocess.run(
        ["git", "-C", str(REPOSITORY), "worktree", "list", "--porcelain"], capture_output=True, text=True, check=True
    ).stdout
    return Path(out.splitlines()[0].split(" ", 1)[1])


def write_run(config_dir: Path) -> None:
    project = config_dir / "projects" / re.sub(r"[^A-Za-z0-9]", "-", str(main_checkout()))
    run = project / "session" / "subagents" / "workflows" / RUN_ID
    run.mkdir(parents=True)
    (run / "journal.jsonl").write_text(json.dumps(STARTED) + "\n", encoding="utf-8")


def report(home: Path, config_dir: Optional[Path]) -> subprocess.CompletedProcess[str]:
    env: Dict[str, str] = {name: value for name, value in os.environ.items() if name != CONFIG_KEY}
    env[HOME_KEY] = str(home)
    if config_dir is not None:
        env[CONFIG_KEY] = str(config_dir)
    command: List[str] = [sys.executable, str(SCRIPT), "once", "--run", RUN_ID]
    return subprocess.run(command, capture_output=True, text=True, env=env, check=False)


class TestProgressConfigDir:
    def test_it_reads_the_runs_of_the_claude_config_dir_when_it_is_set(self, tmp_path: Path) -> None:
        home = tmp_path / "home"
        home.mkdir()
        config_dir = tmp_path / "claude-other-account"
        write_run(config_dir)
        result = report(home, config_dir)
        assert result.returncode == 0, result.stdout + result.stderr
        assert LABEL in result.stdout

    def test_it_reads_the_runs_of_home_dot_claude_without_it(self, tmp_path: Path) -> None:
        home = tmp_path / "home"
        write_run(home / ".claude")
        result = report(home, None)
        assert result.returncode == 0, result.stdout + result.stderr
        assert LABEL in result.stdout

    def test_it_ignores_home_dot_claude_when_the_config_dir_is_set(self, tmp_path: Path) -> None:
        home = tmp_path / "home"
        write_run(home / ".claude")
        result = report(home, tmp_path / "empty-config")
        assert result.returncode == 1
        assert NOT_FOUND in result.stdout
