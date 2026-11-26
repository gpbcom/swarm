from __future__ import annotations

# Standard library imports
from pathlib import Path
from typing import ClassVar, List

# First-party imports
from swarm_models.enums import AppName


class TestSwarmModelsAppEnums:
    APPS_FOLDER: ClassVar[Path] = Path(__file__).resolve().parents[2] / "backend" / "apps"
    NAMES: ClassVar[List[str]] = ["gateway", "fleet", "missions"]

    def test_the_app_names_are_the_apps_of_the_backend(self) -> None:
        folders = sorted(path.name for path in self.APPS_FOLDER.iterdir() if (path / "pyproject.toml").is_file())

        assert sorted(app.value for app in AppName) == folders

    def test_the_values_are_the_folder_names(self) -> None:
        assert [app.value for app in AppName] == self.NAMES
