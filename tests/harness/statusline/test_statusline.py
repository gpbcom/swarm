from __future__ import annotations

# Standard library imports
import json
import os
import subprocess
import sys
from pathlib import Path

GIT_ENV = {
    "GIT_AUTHOR_NAME": "T",
    "GIT_AUTHOR_EMAIL": "t@example.com",
    "GIT_COMMITTER_NAME": "T",
    "GIT_COMMITTER_EMAIL": "t@example.com",
}
SCRIPT = Path(__file__).resolve().parents[3] / ".claude" / "scripts" / "reports" / "statusline.py"
BOARD = {"status": {"T9.01": "running", "T9.02": "review", "T9.03": "done", "T9.04": "ready", "P9": "running"}}


def git(cwd: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, env={**os.environ, **GIT_ENV})


def status_line(cwd: Path) -> str:
    payload = {"workspace": {"current_dir": str(cwd)}, "model": {"display_name": "Opus"}}
    result = subprocess.run(
        [sys.executable, str(SCRIPT)], input=json.dumps(payload), capture_output=True, text=True, check=True
    )
    return result.stdout.strip()


class TestStatusLine:
    def test_it_shows_the_branch_the_open_tickets_and_the_board(self, tmp_path: Path) -> None:
        main = tmp_path / "main"
        main.mkdir()
        git(main, "init", "-b", "develop")
        git(main, "commit", "--allow-empty", "-m", "initial")
        git(main, "worktree", "add", "-b", "feature/T9.01", str(tmp_path / "T9.01"))
        (main / ".git" / "swarm").mkdir()
        (main / ".git" / "swarm" / "board.json").write_text(json.dumps(BOARD), encoding="utf-8")
        line = status_line(tmp_path / "T9.01")
        assert line.startswith("🌿 feature/T9.01")
        assert "🎫 T9.01 🔄" in line
        assert "open 🔄T9.01" in line
        assert "✅1 📝0 🔄1 👀1 🏁1/4" in line
        assert line.endswith("🧠 Opus")

    def test_it_shows_the_tickets_running_in_the_shared_checkout(self, tmp_path: Path) -> None:
        main = tmp_path / "main"
        main.mkdir()
        git(main, "init", "-b", "develop")
        git(main, "commit", "--allow-empty", "-m", "initial")
        git(main, "checkout", "-b", "feature/tickets")
        for ticket in ("T9.01", "T9.02"):
            (main / ".git" / "swarm" / ticket).mkdir(parents=True)
            (main / ".git" / "swarm" / ticket / "state.json").write_text("{}", encoding="utf-8")
        (main / ".git" / "swarm" / "board.json").write_text(json.dumps(BOARD), encoding="utf-8")
        line = status_line(main)
        assert line.startswith("🌿 feature/tickets")
        assert "open 🔄T9.01 👀T9.02" in line

    def test_it_never_fails_outside_a_repository(self, tmp_path: Path) -> None:
        assert status_line(tmp_path).startswith("🔀")
