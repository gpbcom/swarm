from __future__ import annotations

# Standard library imports
import json
from pathlib import Path
from typing import List

# Third-party imports
from pydantic import JsonValue

# First-party imports
from tests.harness.checks.helpers import call

E2E_MANIFEST = {"name": "@swarm/ground-control", "scripts": {"e2e": "playwright test"}}


def a_front_end(root: Path, name: str, dockerfile: bool = True) -> None:
    folder = root / "frontend" / "apps" / name
    folder.mkdir(parents=True)
    (folder / "package.json").write_text(json.dumps(E2E_MANIFEST), encoding="utf-8")
    if dockerfile:
        (folder / "Dockerfile").write_text("FROM scratch\n", encoding="utf-8")


def image_run(root: Path, changed: List[str]) -> List[JsonValue]:
    setup = (
        f"checks.ROOT = Path({str(root)!r}); commands = []\n"
        "checks.run = lambda command, cwd=None, env=None: (commands.append([*command, str(env)]) or (0, ''))\n"
        f"verdict = checks.run_image_checks('T9.05', {changed!r}, Path({str(root)!r}))"
    )
    value = call("[commands, verdict]", setup)
    assert isinstance(value, list)
    return value


class TestChecksImages:
    def test_a_changed_front_end_is_built_and_tested_against_its_image(self, tmp_path: Path) -> None:
        a_front_end(tmp_path, "ground-control")
        commands, verdict = image_run(tmp_path, ["frontend/apps/ground-control/src/app.tsx"])
        build = ["docker", "build", "-f", "frontend/apps/ground-control/Dockerfile"]
        assert any(
            command[:4] == build and "ghcr.io/gpbcom/swarm/ground-control:local" in command for command in commands
        )
        [e2e] = [command for command in commands if "e2e" in command]
        assert e2e[:5] == ["pnpm", "--filter", "@swarm/ground-control", "run", "e2e"]
        assert "'SWARM_IMAGE_TAG': 'local'" in e2e[-1]
        assert verdict["passed"] is True

    def test_a_front_end_without_an_image_is_not_applicable(self, tmp_path: Path) -> None:
        a_front_end(tmp_path, "mission-studio", dockerfile=False)
        commands, verdict = image_run(tmp_path, ["frontend/apps/mission-studio/src/app.tsx"])
        assert commands == []
        assert verdict["not_applicable"] == ["images: no front end with an image and an e2e suite changed"]

    def test_the_main_checks_never_build_images(self, tmp_path: Path) -> None:
        a_front_end(tmp_path, "ground-control")
        setup = (
            f"checks.ROOT = Path({str(tmp_path)!r}); commands = []\n"
            "checks.run = lambda command, cwd=None, env=None: (commands.append(command) or (0, ''))\n"
            f"c = checks.Checks('T9.05', Path({str(tmp_path)!r}))\n"
            "checks.typescript_checks(c, ['frontend/apps/ground-control/src/app.tsx'])"
        )
        assert not any("docker" in command for command in call("commands", setup))


class TestChecksPostgres:
    def postgres_run(self, root: Path, changed: List[str], installed: bool) -> List[JsonValue]:
        setup = (
            f"checks.ROOT = Path({str(root)!r})\n"
            f"checks.postgres_binaries = lambda: {installed!r}\n"
            f"c = checks.Checks('T9.05', Path({str(root)!r}))\n"
            f"checks.postgres_checks(c, {changed!r})"
        )
        value = call("[c.failures, c.passed, c.not_applicable]", setup)
        assert isinstance(value, list)
        return value

    def test_a_migration_without_postgresql_binaries_stops_on_the_environment(self, tmp_path: Path) -> None:
        migration = "backend/apps/gateway/migrations/versions/0002_operators.py"
        failures, _, _ = self.postgres_run(tmp_path, [migration], installed=False)
        assert isinstance(failures, list)
        [failure] = failures
        assert failure["file"] == migration
        assert failure["environment"] is True
        assert "L-53" in failure["detail"]

    def test_storage_code_with_the_binaries_passes(self, tmp_path: Path) -> None:
        changed = ["backend/swarm-storage/src/swarm_storage/gateway/operator_repository.py"]
        failures, passed, _ = self.postgres_run(tmp_path, changed, installed=True)
        assert failures == []
        assert passed == ["postgresql binaries"]

    def test_a_ticket_without_migration_or_storage_code_needs_no_postgresql(self, tmp_path: Path) -> None:
        failures, _, skipped = self.postgres_run(tmp_path, ["frontend/apps/back-office/src/app.tsx"], installed=False)
        assert failures == []
        assert skipped == ["postgresql: no migration and no storage code changed"]
