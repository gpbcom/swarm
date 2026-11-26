from __future__ import annotations

# Standard library imports
from pathlib import Path
from typing import ClassVar, Dict, List, Optional

# Third-party imports
import pytest
from pydantic import JsonValue, ValidationError

# First-party imports
from fleet.models.config.exceptions import (
    SEFleetConfigInvalidPostgres,
    SEFleetConfigInvalidRest,
    SEFleetConfigInvalidSchemaName,
    SEFleetConfigUnreadable,
    SEInvalidFleetConfigException,
)
from fleet.models.config.fleet_config import FleetConfig
from swarm_models.config.postgres.postgres_config import PostgresConfig
from swarm_web.models.config.rest_config import RestConfig


class TestFleetConfig:
    SERVICE_FOLDER: ClassVar[Path] = Path(__file__).resolve().parents[3]
    OTHER_DSN_KEY: ClassVar[str] = "SWARM_OTHER_POSTGRES_DSN"
    UNKNOWN_KEY_CONFIGURATION: ClassVar[Dict[str, JsonValue]] = {"colour": "red"}
    FIELD_ERRORS: ClassVar[List[type[Exception]]] = [
        SEFleetConfigInvalidSchemaName,
        SEFleetConfigInvalidPostgres,
        SEFleetConfigInvalidRest,
    ]

    def test_defaults(self) -> None:
        config = FleetConfig()
        assert config.schema_name == "fleet"
        assert config.postgres == PostgresConfig(dsn_key=FleetConfig.DSN_KEY)
        assert config.rest == RestConfig()

    def test_the_class_constants(self) -> None:
        assert FleetConfig.UNREADABLE is SEFleetConfigUnreadable
        assert not issubclass(SEFleetConfigUnreadable, ValueError)
        assert FleetConfig.APP_FILE == "app.yaml"
        assert FleetConfig.LOGGER_FILE == "logger.yaml"
        assert FleetConfig.DSN_KEY == "SWARM_FLEET_POSTGRES_DSN"

    def test_the_home_entry_moves_the_conf_and_migrations_folders(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        monkeypatch.setenv(FleetConfig.HOME_KEY, str(tmp_path))
        assert FleetConfig.conf_folder() == tmp_path / FleetConfig.CONF_FOLDER_NAME
        assert FleetConfig.migrations_folder() == tmp_path / FleetConfig.MIGRATIONS_FOLDER_NAME

    @pytest.mark.parametrize("home", [None, "", "   "])
    def test_an_unset_or_blank_home_entry_leaves_the_folders_of_the_repository(
        self, monkeypatch: pytest.MonkeyPatch, home: Optional[str]
    ) -> None:
        if home is None:
            monkeypatch.delenv(FleetConfig.HOME_KEY, raising=False)
        else:
            monkeypatch.setenv(FleetConfig.HOME_KEY, home)
        service_folder = Path(__file__).resolve().parents[3]
        assert FleetConfig.conf_folder().resolve() == service_folder / FleetConfig.CONF_FOLDER_NAME
        assert FleetConfig.migrations_folder().resolve() == service_folder / FleetConfig.MIGRATIONS_FOLDER_NAME

    def test_the_conf_folder_is_the_conf_folder_of_the_service(self) -> None:
        assert FleetConfig.conf_folder().resolve() == self.SERVICE_FOLDER / "conf"

    def test_full_valid_construction(self) -> None:
        postgres = PostgresConfig(dsn_key=self.OTHER_DSN_KEY)
        config = FleetConfig(schema_name="fleet_2", postgres=postgres, rest=RestConfig())
        assert config.schema_name == "fleet_2"
        assert config.postgres == postgres
        assert config.rest == RestConfig()

    @pytest.mark.parametrize("name", ["schema_name", "postgres", "rest"])
    def test_none_becomes_the_default(self, name: str) -> None:
        config = FleetConfig.model_validate({name: None})
        default = FleetConfig.model_fields[name].get_default(call_default_factory=True)
        assert getattr(config, name) == default

    @pytest.mark.parametrize(
        ("name", "value", "error"),
        [
            ("schema_name", "", SEFleetConfigInvalidSchemaName),
            ("schema_name", "   ", SEFleetConfigInvalidSchemaName),
            ("schema_name", 3, SEFleetConfigInvalidSchemaName),
            ("schema_name", True, SEFleetConfigInvalidSchemaName),
            ("schema_name", "Fleet", SEFleetConfigInvalidSchemaName),
            ("schema_name", "1fleet", SEFleetConfigInvalidSchemaName),
            ("schema_name", "fleet-2", SEFleetConfigInvalidSchemaName),
            ("schema_name", "fleet 2", SEFleetConfigInvalidSchemaName),
            ("postgres", 3, SEFleetConfigInvalidPostgres),
            ("postgres", "dsn", SEFleetConfigInvalidPostgres),
            ("postgres", ["dsn"], SEFleetConfigInvalidPostgres),
            ("rest", 3, SEFleetConfigInvalidRest),
            ("rest", "rest", SEFleetConfigInvalidRest),
            ("rest", ["rest"], SEFleetConfigInvalidRest),
        ],
    )
    def test_rejects_bad_values(self, name: str, value: JsonValue, error: type[Exception]) -> None:
        with pytest.raises(error):
            FleetConfig.model_validate({name: value})

    @pytest.mark.parametrize("error", FIELD_ERRORS)
    def test_the_field_exceptions_share_the_model_base(self, error: type[Exception]) -> None:
        assert issubclass(error, SEInvalidFleetConfigException)

    def test_a_schema_name_with_surrounding_spaces_is_stripped(self) -> None:
        assert FleetConfig(schema_name="  fleet_2  ").schema_name == "fleet_2"

    def test_a_mapping_becomes_the_nested_model(self) -> None:
        data: Dict[str, JsonValue] = {"postgres": PostgresConfig(dsn_key=self.OTHER_DSN_KEY).model_dump()}
        config = FleetConfig.model_validate(data)
        assert config.postgres == PostgresConfig(dsn_key=self.OTHER_DSN_KEY)

    def test_rejects_unknown_keys(self) -> None:
        with pytest.raises(ValidationError):
            FleetConfig.model_validate(self.UNKNOWN_KEY_CONFIGURATION)

    def test_round_trip(self) -> None:
        config = FleetConfig(schema_name="fleet_2")
        data: Dict[str, JsonValue] = config.model_dump()
        assert FleetConfig.model_validate(data) == config

    def test_loading_app_yaml_equals_the_defaults(self) -> None:
        assert FleetConfig.load(FleetConfig.conf_folder() / FleetConfig.APP_FILE) == FleetConfig()

    def test_an_unreadable_file_raises_the_unreadable_exception(self, tmp_path: Path) -> None:
        with pytest.raises(SEFleetConfigUnreadable):
            FleetConfig.load(tmp_path / FleetConfig.APP_FILE)
