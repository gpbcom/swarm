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
            check=False,
        )
        assert result.returncode == 0, result.stderr
        assert result.stdout.splitlines()[-1] == "8 phases, 68 epics, 262 tickets, 595 blocked-by"


GIT_ENV = {
    "GIT_AUTHOR_NAME": "T",
    "GIT_AUTHOR_EMAIL": "t@example.com",
    "GIT_COMMITTER_NAME": "T",
    "GIT_COMMITTER_EMAIL": "t@example.com",
}


def git(cwd: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, env={**os.environ, **GIT_ENV})


def develop_ref(repo: Path) -> str:
    code = f"import sys; sys.path.insert(0, {str(SCRIPT.parent)!r}); import roadmap_gantt; print(roadmap_gantt.develop_ref({str(repo)!r}))"
    return subprocess.run(
        [sys.executable, "-c", code], cwd=ROOT, capture_output=True, text=True, check=True
    ).stdout.strip()


class TestDevelopRef:
    def test_the_local_develop_comes_first(self, tmp_path: Path) -> None:
        git(tmp_path, "init", "-b", "develop")
        git(tmp_path, "commit", "--allow-empty", "-m", "one")
        assert develop_ref(tmp_path) == "develop"

    def test_a_checkout_without_develop_uses_origin_develop(self, tmp_path: Path) -> None:
        origin = tmp_path / "origin"
        origin.mkdir()
        git(origin, "init", "-b", "develop")
        git(origin, "commit", "--allow-empty", "-m", "one")
        git(tmp_path, "clone", "--quiet", str(origin), "clone")
        clone = tmp_path / "clone"
        git(clone, "checkout", "--quiet", "--detach")
        git(clone, "branch", "-D", "develop")
        assert develop_ref(clone) == "origin/develop"

    def test_a_ci_checkout_of_a_pull_request_uses_its_own_commit(self, tmp_path: Path) -> None:
        git(tmp_path, "init", "-b", "pull-request")
        git(tmp_path, "commit", "--allow-empty", "-m", "one")
        assert develop_ref(tmp_path) == "HEAD"
