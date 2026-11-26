from __future__ import annotations

# Standard library imports
from pathlib import Path
from typing import Optional

# Third-party imports
import pytest

# First-party imports
from swarm_catalog.models.yaml_catalog import YamlCatalog
from swarm_models.config.app_config import AppConfig


class TestAppConfig:
    def test_it_is_a_yaml_catalog(self) -> None:
        assert issubclass(AppConfig, YamlCatalog)

    def test_the_constants_name_the_entry_the_folders_and_the_files(self) -> None:
        assert AppConfig.APP_ROOT_KEY == "SWARM_APP_ROOT"
        assert AppConfig.CONF_FOLDER == "conf"
        assert AppConfig.APP_FILE == "app.yaml"
        assert AppConfig.LOGGER_FILE == "logger.yaml"
        assert AppConfig.MIGRATIONS_FOLDER == "migrations"

    def test_the_app_root_entry_names_the_app_folder(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        monkeypatch.setenv(AppConfig.APP_ROOT_KEY, f"  {tmp_path}  ")

        assert AppConfig.app_folder() == tmp_path
        assert AppConfig.conf_folder() == tmp_path / AppConfig.CONF_FOLDER
        assert AppConfig.migrations_folder() == tmp_path / AppConfig.MIGRATIONS_FOLDER

    @pytest.mark.parametrize("root", [None, "", "   "])
    def test_an_unset_or_blank_entry_gives_the_current_folder(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path, root: Optional[str]
    ) -> None:
        if root is None:
            monkeypatch.delenv(AppConfig.APP_ROOT_KEY, raising=False)
        else:
            monkeypatch.setenv(AppConfig.APP_ROOT_KEY, root)
        monkeypatch.chdir(tmp_path)

        assert AppConfig.app_folder() == tmp_path

    def test_a_relative_path_of_the_configuration_is_read_in_the_app_folder(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        monkeypatch.setenv(AppConfig.APP_ROOT_KEY, str(tmp_path))

        assert AppConfig.in_app_folder("conf/catalogs/a.yaml") == tmp_path / "conf" / "catalogs" / "a.yaml"

    def test_an_absolute_path_of_the_configuration_is_kept(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        monkeypatch.setenv(AppConfig.APP_ROOT_KEY, str(tmp_path / "app"))

        assert AppConfig.in_app_folder(str(tmp_path / "a.yaml")) == tmp_path / "a.yaml"
