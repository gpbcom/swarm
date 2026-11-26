from __future__ import annotations

# Standard library imports
from pathlib import Path
from typing import ClassVar

# Third-party imports
import pytest
from fastapi import FastAPI

# First-party imports
from swarm_models.config.app_config import AppConfig
from swarm_models.config.gateway.gateway_config import GatewayConfig
from swarm_models.enums import AppName
from swarm_scripts.repository_paths import RepositoryPaths
from swarm_scripts.swarm_apps import SwarmApps


class TestSwarmApps:
    UNKNOWN_APP: ClassVar[str] = "nowhere"

    @pytest.fixture(autouse=True)
    def no_entries(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv(SwarmApps.APP_KEY, raising=False)
        monkeypatch.delenv(AppConfig.APP_ROOT_KEY, raising=False)

    def test_the_app_entry_is_swarm_app(self) -> None:
        assert SwarmApps.APP_KEY == "SWARM_APP"

    def test_every_app_has_its_configuration_and_its_application(self) -> None:
        assert set(SwarmApps.CONFIGS) == set(AppName)
        assert set(SwarmApps.APPLICATIONS) == set(AppName)

    @pytest.mark.parametrize("app", list(AppName))
    def test_each_application_is_a_fastapi_application(self, app: AppName) -> None:
        assert isinstance(SwarmApps.APPLICATIONS[app](), FastAPI)

    def test_without_the_entry_every_app_is_selected(self) -> None:
        assert SwarmApps().requested() is None
        assert SwarmApps().selected() == list(AppName)

    def test_the_entry_selects_one_app(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv(SwarmApps.APP_KEY, f"  {AppName.MISSIONS.value}  ")

        assert SwarmApps().selected() == [AppName.MISSIONS]

    def test_an_unknown_app_selects_none(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv(SwarmApps.APP_KEY, self.UNKNOWN_APP)

        assert SwarmApps().requested() == self.UNKNOWN_APP
        assert SwarmApps().selected() == []

    @pytest.mark.parametrize("app", list(AppName))
    def test_without_the_entries_the_folder_is_the_one_of_the_repository(self, app: AppName) -> None:
        folder = SwarmApps().folder(app)

        assert folder == RepositoryPaths.APPS / app.value
        assert (folder / AppConfig.CONF_FOLDER / AppConfig.APP_FILE).is_file()
        assert (folder / AppConfig.MIGRATIONS_FOLDER).is_dir()

    def test_the_app_root_names_the_folder_of_the_app_the_entry_names(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        monkeypatch.setenv(SwarmApps.APP_KEY, AppName.GATEWAY.value)
        monkeypatch.setenv(AppConfig.APP_ROOT_KEY, str(tmp_path))

        assert SwarmApps().folder(AppName.GATEWAY) == tmp_path
        assert SwarmApps().folder(AppName.FLEET) == RepositoryPaths.APPS / AppName.FLEET.value

    def test_the_app_root_alone_names_no_folder(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        monkeypatch.setenv(AppConfig.APP_ROOT_KEY, str(tmp_path))

        assert SwarmApps().folder(AppName.GATEWAY) == RepositoryPaths.APPS / AppName.GATEWAY.value

    @pytest.mark.parametrize("app", list(AppName))
    def test_each_configuration_loads_from_the_app_yaml_of_its_app(self, app: AppName) -> None:
        config = SwarmApps().config(app)

        assert isinstance(config, SwarmApps.CONFIGS[app])
        assert config.schema_name == app.value

    def test_the_gateway_configuration_is_its_default(self) -> None:
        assert SwarmApps().config(AppName.GATEWAY) == GatewayConfig()
