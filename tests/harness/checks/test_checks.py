from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import List

ROOT = Path(__file__).resolve().parents[3]
GIT_ENV = {
    "GIT_AUTHOR_NAME": "T",
    "GIT_AUTHOR_EMAIL": "t@example.com",
    "GIT_COMMITTER_NAME": "T",
    "GIT_COMMITTER_EMAIL": "t@example.com",
}
TICKET = "T9.01"


def git(cwd: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, env={**os.environ, **GIT_ENV})


def changed(repo: Path) -> List[str]:
    code = (
        f"import sys; sys.path.insert(0, {str(ROOT / '.claude' / 'scripts')!r}); import checks; "
        f"print('\\n'.join(checks.changed_files('develop', {TICKET!r}, __import__('pathlib').Path({str(repo)!r}))))"
    )
    result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, check=True)
    return [line for line in result.stdout.splitlines() if line]


def two_tickets_at_work(tmp_path: Path, paths: object) -> Path:
    git(tmp_path, "init", "-b", "develop")
    (tmp_path / "base.txt").write_text("base\n", encoding="utf-8")
    git(tmp_path, "add", "-A")
    git(tmp_path, "commit", "-m", "base")
    for name in ("services/mine/a.py", "services/theirs/b.py", f"docs/tickets/{TICKET}/TICKET.md"):
        (tmp_path / name).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / name).write_text("x = 1\n", encoding="utf-8")
    state = tmp_path / ".git" / "swarm" / TICKET
    state.mkdir(parents=True)
    (state / "state.json").write_text(json.dumps({"ticket": TICKET, "paths": paths}), encoding="utf-8")
    return tmp_path


class TestChecks:
    def test_a_ticket_is_checked_on_its_own_files_only(self, tmp_path: Path) -> None:
        repo = two_tickets_at_work(tmp_path, ["services/mine/a.py", f"docs/tickets/{TICKET}/"])
        assert changed(repo) == [f"docs/tickets/{TICKET}/TICKET.md", "services/mine/a.py"]

    def test_a_ticket_without_recorded_files_is_checked_on_every_change(self, tmp_path: Path) -> None:
        repo = two_tickets_at_work(tmp_path, None)
        assert "services/theirs/b.py" in changed(repo)
