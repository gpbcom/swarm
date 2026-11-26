from __future__ import annotations

# Standard library imports
from pathlib import Path
from typing import ClassVar, List

# First-party imports
from swarm_models.enums import AppName


class TestSwarmModelsAppEnums:
    APPS_FOLDER: ClassVar[Path] = Path(__file__).resolve().parents[2] / "backend" / "apps"
    NAMES: ClassVar[List[str]] = ["gateway", "fleet", "missions", "simulator", "flight_engine"]
    HYPHEN: ClassVar[str] = "-"
    UNDERSCORE: ClassVar[str] = "_"

    def test_the_app_names_are_the_apps_of_the_backend_with_underscores(self) -> None:
        folders = sorted(
            path.name.replace(self.HYPHEN, self.UNDERSCORE)
            for path in self.APPS_FOLDER.iterdir()
            if (path / "pyproject.toml").is_file()
        )

        assert sorted(app.value for app in AppName) == folders

    def test_the_values_are_the_folder_names_with_underscores(self) -> None:
        assert [app.value for app in AppName] == self.NAMES
