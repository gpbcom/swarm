from __future__ import annotations

# Standard library imports
from pathlib import Path
from typing import List

# First-party imports
from tests.harness.checks.helpers import call


def python_run(root: Path) -> List[List[str]]:
    setup = (
        f"checks.ROOT = Path({str(root)!r}); commands = []\n"
        "checks.run = lambda command, cwd=None, env=None: (commands.append(command) or (0, ''))\n"
        f"c = checks.Checks('T9.03', Path({str(root)!r}))\n"
        "checks.install_swarm_core = lambda checks_: None\n"
        "checks.python_checks(c, ['tests/a/test_a.py'])"
    )
    value = call("[commands, c.not_applicable]", setup)
    assert isinstance(value, list)
    return value


def tree(root: Path, *folders: str) -> Path:
    (root / "tests" / "a").mkdir(parents=True)
    (root / "tests" / "a" / "test_a.py").write_text("", encoding="utf-8")
    for folder in folders:
        (root / folder).mkdir(parents=True)
    return root


class TestChecksPython:
    def test_pytest_runs_on_two_workers_as_ci_does(self, tmp_path: Path) -> None:
        commands, _ = python_run(tree(tmp_path))
        assert ["uv", "run", "pytest", "-q", "-n", "2"] in commands

    def test_mypy_is_skipped_with_its_reason_when_no_source_folder_exists(self, tmp_path: Path) -> None:
        commands, skipped = python_run(tree(tmp_path))
        assert not any("mypy" in command for command in commands)
        assert any(entry.startswith("mypy: not run") for entry in skipped)

    def test_mypy_reads_the_layers_the_libs_the_apps_and_the_scripts(self, tmp_path: Path) -> None:
        folders = ("backend/swarm-service/src", "backend/libs/swarm-web/src", "backend/apps/gateway/src", "scripts/src")
        commands, skipped = python_run(tree(tmp_path, *folders))
        mypy = next(command for command in commands if "mypy" in command)
        assert set(folders) <= set(mypy)
        assert skipped == []
