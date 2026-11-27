from __future__ import annotations

# Standard library imports
from pathlib import Path
from typing import ClassVar, Dict, Optional

# Third-party imports
import pytest
from pydantic import JsonValue

# First-party imports
from swarm_catalog.models.yaml_catalog import YamlCatalog
from swarm_models.config.app_config import AppConfig
from swarm_models.config.exceptions import SEAppConfigInvalidSignals
from swarm_web.models.config.exceptions import SESignalsConfigInvalidMetricsInterval
from swarm_web.models.config.signals_config import SignalsConfig


class TestAppConfig:
    SIGNALS: ClassVar[Dict[str, JsonValue]] = {"enabled": True, "cell": "eu_west", "metrics_interval_s": 15.0}

    def test_the_signals_default_to_a_default_signals_config(self) -> None:
        assert AppConfig().signals == SignalsConfig()

    def test_a_signals_mapping_becomes_a_signals_config(self) -> None:
        config = AppConfig.model_validate({"signals": self.SIGNALS})
        assert config.signals == SignalsConfig(enabled=True, cell="eu_west", metrics_interval_s=15.0)

    def test_a_signals_config_is_kept(self) -> None:
        signals = SignalsConfig(enabled=True)
        assert AppConfig(signals=signals).signals == signals

    def test_none_becomes_the_default_signals(self) -> None:
        assert AppConfig.model_validate({"signals": None}).signals == SignalsConfig()

    @pytest.mark.parametrize("value", ["on", 3, True, [1], 1.5])
    def test_signals_that_are_not_a_mapping_are_refused(self, value: JsonValue) -> None:
        with pytest.raises(SEAppConfigInvalidSignals):
            AppConfig.model_validate({"signals": value})

    def test_a_signals_error_is_raised_unchanged(self) -> None:
        with pytest.raises(SESignalsConfigInvalidMetricsInterval):
            AppConfig.model_validate({"signals": {"metrics_interval_s": 0}})

    def test_the_signals_round_trip(self) -> None:
        config = AppConfig.model_validate({"signals": self.SIGNALS})
        assert AppConfig.model_validate(config.model_dump()) == config

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
