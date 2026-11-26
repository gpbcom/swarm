from __future__ import annotations

# Standard library imports
import json
from typing import Dict, List

# Third-party imports
import pytest
from pydantic import JsonValue

# First-party imports
from tests.conventions.mono_repo.helpers import repo_root


class TestPnpmWorkspace:
    def load_json(self, name: str) -> Dict[str, JsonValue]:
        path = repo_root() / name
        assert path.is_file(), f"{name} is missing."
        return json.loads(path.read_text(encoding="utf-8"))

    def workspace_entries(self) -> List[str]:
        path = repo_root() / "pnpm-workspace.yaml"
        assert path.is_file(), "pnpm-workspace.yaml is missing."
        entries: List[str] = []
        for line in path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if stripped.startswith("- "):
                entries.append(stripped[2:].strip().strip("'\""))
        return entries

    def test_the_root_package_is_private(self) -> None:
        assert self.load_json("package.json").get("private") is True

    def test_the_root_package_pins_pnpm(self) -> None:
        assert str(self.load_json("package.json").get("packageManager", "")).startswith("pnpm@")

    def test_the_root_package_depends_on_turbo(self) -> None:
        assert "turbo" in self.load_json("package.json").get("devDependencies", {})

    @pytest.mark.parametrize("entry", ["frontend/apps/*", "frontend/packages/*", "qa/e2e"])
    def test_the_workspace_lists_its_folders(self, entry: str) -> None:
        assert entry in self.workspace_entries()

    @pytest.mark.parametrize("task", ["build", "lint", "typecheck", "test"])
    def test_turbo_defines_the_task(self, task: str) -> None:
        assert task in self.load_json("turbo.json").get("tasks", {})

    def test_the_lock_file_is_at_the_root(self) -> None:
        assert (repo_root() / "pnpm-lock.yaml").is_file()

    @pytest.mark.parametrize("folder", ["frontend/apps", "frontend/packages", "qa/e2e"])
    def test_the_workspace_folder_exists(self, folder: str) -> None:
        assert (repo_root() / folder).is_dir()
