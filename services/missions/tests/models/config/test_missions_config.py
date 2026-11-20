from __future__ import annotations

from pathlib import Path
from typing import ClassVar, Dict, List

import pytest
from pydantic import JsonValue, ValidationError

from missions.models.config.exceptions import (
    SEInvalidMissionsConfigException,
    SEMissionsConfigInvalidPostgres,
    SEMissionsConfigInvalidRest,
    SEMissionsConfigInvalidSchemaName,
    SEMissionsConfigUnreadable,
)
from missions.models.config.missions_config import MissionsConfig
from swarm_rest.models.config.rest_config import RestConfig
from swarm_storage.models.config.postgres_config import PostgresConfig


class TestMissionsConfig:
    CONF_FOLDER: ClassVar[Path] = Path(__file__).resolve().parents[3] / "conf"
    FIELD_ERRORS: ClassVar[List[type[Exception]]] = [
        SEMissionsConfigInvalidSchemaName,
        SEMissionsConfigInvalidPostgres,
        SEMissionsConfigInvalidRest,
    ]
    UNKNOWN_KEY_CONFIGURATION: ClassVar[Dict[str, JsonValue]] = {"colour": "red"}
    FULL_CONFIGURATION: ClassVar[Dict[str, JsonValue]] = {
        "schema_name": "missions_two",
        "postgres": {"dsn_key": "SWARM_OTHER_DSN"},
        "rest": {"port": 9000},
    }
    NESTED_ERROR_CONFIGURATIONS: ClassVar[List[Dict[str, JsonValue]]] = [
        {"postgres": {"dsn_key": ""}},
        {"rest": {"port": 0}},
    ]

    def test_defaults(self) -> None:
        config = MissionsConfig()
        assert config.schema_name == "missions"
        assert config.postgres == PostgresConfig(dsn_key=MissionsConfig.DSN_KEY)
        assert config.rest == RestConfig()

    def test_full_valid_construction(self) -> None:
        config = MissionsConfig.model_validate(self.FULL_CONFIGURATION)
        assert config.schema_name == "missions_two"
        assert config.postgres == PostgresConfig(dsn_key="SWARM_OTHER_DSN")
        assert config.rest == RestConfig(port=9000)

    @pytest.mark.parametrize("name", ["schema_name", "postgres", "rest"])
    def test_none_becomes_the_default(self, name: str) -> None:
        config = MissionsConfig.model_validate({name: None})
        default = MissionsConfig.model_fields[name].get_default(call_default_factory=True)
        assert getattr(config, name) == default

    @pytest.mark.parametrize(
        ("name", "value", "error"),
        [
            ("schema_name", "", SEMissionsConfigInvalidSchemaName),
            ("schema_name", "   ", SEMissionsConfigInvalidSchemaName),
            ("schema_name", "Demo", SEMissionsConfigInvalidSchemaName),
            ("schema_name", "1a", SEMissionsConfigInvalidSchemaName),
            ("schema_name", "x;drop", SEMissionsConfigInvalidSchemaName),
            ("schema_name", 3, SEMissionsConfigInvalidSchemaName),
            ("schema_name", True, SEMissionsConfigInvalidSchemaName),
            ("postgres", 3, SEMissionsConfigInvalidPostgres),
            ("postgres", "dsn", SEMissionsConfigInvalidPostgres),
            ("postgres", ["dsn"], SEMissionsConfigInvalidPostgres),
            ("rest", 3, SEMissionsConfigInvalidRest),
            ("rest", "rest", SEMissionsConfigInvalidRest),
            ("rest", ["rest"], SEMissionsConfigInvalidRest),
        ],
    )
    def test_rejects_bad_values(self, name: str, value: JsonValue, error: type[Exception]) -> None:
        with pytest.raises(error):
            MissionsConfig.model_validate({name: value})

    def test_rejects_unknown_keys(self) -> None:
        with pytest.raises(ValidationError):
            MissionsConfig.model_validate(self.UNKNOWN_KEY_CONFIGURATION)

    def test_round_trip(self) -> None:
        config = MissionsConfig.model_validate(self.FULL_CONFIGURATION)
        data: Dict[str, JsonValue] = config.model_dump()
        assert MissionsConfig.model_validate(data) == config

    @pytest.mark.parametrize("error", FIELD_ERRORS)
    def test_the_field_exceptions_share_the_model_base(self, error: type[Exception]) -> None:
        assert issubclass(error, SEInvalidMissionsConfigException)

    @pytest.mark.parametrize("configuration", NESTED_ERROR_CONFIGURATIONS)
    def test_the_errors_of_a_nested_model_are_raised_unchanged(self, configuration: Dict[str, JsonValue]) -> None:
        with pytest.raises(Exception) as raised:
            MissionsConfig.model_validate(configuration)
        assert not isinstance(raised.value, (SEMissionsConfigInvalidPostgres, SEMissionsConfigInvalidRest))

    def test_a_schema_name_with_surrounding_spaces_is_stripped(self) -> None:
        assert MissionsConfig(schema_name="  missions  ").schema_name == "missions"

    def test_the_constants_name_the_files_and_the_dsn_entry(self) -> None:
        assert MissionsConfig.UNREADABLE is SEMissionsConfigUnreadable
        assert MissionsConfig.APP_FILE == "app.yaml"
        assert MissionsConfig.LOGGER_FILE == "logger.yaml"
        assert MissionsConfig.DSN_KEY == "SWARM_MISSIONS_POSTGRES_DSN"

    def test_the_unreadable_error_is_not_a_value_error(self) -> None:
        assert not issubclass(SEMissionsConfigUnreadable, ValueError)

    def test_the_conf_folder_is_the_one_of_the_service(self) -> None:
        assert MissionsConfig.conf_folder().resolve() == self.CONF_FOLDER

    def test_the_app_file_writes_every_default_out(self) -> None:
        loaded = MissionsConfig.load(MissionsConfig.conf_folder() / MissionsConfig.APP_FILE)
        assert loaded == MissionsConfig()

    def test_a_missing_file_is_unreadable(self, tmp_path: Path) -> None:
        with pytest.raises(SEMissionsConfigUnreadable):
            MissionsConfig.load(tmp_path / MissionsConfig.APP_FILE)
