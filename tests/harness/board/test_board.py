from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / ".claude" / "scripts" / "board.py"
TAKEN = "Validation failed: Target issue has already been taken"
PROBE = (
    "import sys; sys.path.insert(0, {scripts!r}); import board; "
    "print(board.gh(['api', 'graphql'], {{}}, tolerate_existing={tolerate}))"
)


def fake_gh(folder: Path, message: str) -> Path:
    """Write a ``gh`` that fails like GitHub does when a link already exists."""
    folder.mkdir()
    gh = folder / "gh"
    gh.write_text(f"#!/bin/sh\necho 'gh: {message}' >&2\nexit 1\n", encoding="utf-8")
    gh.chmod(0o755)
    return folder


def probe(tmp_path: Path, tolerate: bool, message: str = TAKEN) -> subprocess.CompletedProcess[str]:
    path = fake_gh(tmp_path / "bin", message)
    code = PROBE.format(scripts=str(SCRIPT.parent), tolerate=tolerate)
    return subprocess.run(
        [sys.executable, "-c", code],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        env={**os.environ, "PATH": f"{path}{os.pathsep}{os.environ['PATH']}"},
    )


class TestBoard:
    def test_a_link_made_before_a_stop_counts_as_made_on_resume(self, tmp_path: Path) -> None:
        result = probe(tmp_path, tolerate=True)
        assert result.returncode == 0, result.stderr
        assert result.stdout.strip() == "None"

    def test_an_existing_link_is_still_an_error_when_not_expected(self, tmp_path: Path) -> None:
        assert probe(tmp_path, tolerate=False).returncode != 0

    @pytest.mark.parametrize("message", ["Could not resolve to a node", "Bad credentials"])
    def test_any_other_error_stops_the_bootstrap(self, tmp_path: Path, message: str) -> None:
        result = probe(tmp_path, tolerate=True, message=message)
        assert result.returncode != 0
        assert message in result.stderr

    def test_the_dry_run_counts_every_phase_epic_ticket_and_link(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "bootstrap", "--dry-run"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        assert result.stdout.splitlines()[-1] == "8 phases, 68 epics, 262 tickets, 595 blocked-by"
