from __future__ import annotations

# Standard library imports
from pathlib import Path
from typing import ClassVar, Dict, List

# Third-party imports
import pytest
from pydantic import JsonValue, ValidationError

# First-party imports
from swarm_catalog.models.yaml_catalog import YamlCatalog
from swarm_models.config.gateway.exceptions import (
    SEGatewayConfigInvalidPostgres,
    SEGatewayConfigInvalidRest,
    SEGatewayConfigInvalidSchemaName,
    SEGatewayConfigUnreadable,
    SEInvalidGatewayConfigException,
)
from swarm_models.config.gateway.gateway_config import GatewayConfig
from swarm_models.config.postgres.exceptions import SEPostgresConfigInvalidDsnKey
from swarm_models.config.postgres.postgres_config import PostgresConfig
from swarm_web.models.config.exceptions import SERestConfigInvalidPort
from swarm_web.models.config.rest_config import RestConfig


class TestGatewayConfig:
    APP_FOLDER: ClassVar[Path] = Path(__file__).resolve().parents[4] / "backend" / "apps" / "gateway"
    FIELD_ERRORS: ClassVar[List[type[Exception]]] = [
        SEGatewayConfigInvalidSchemaName,
        SEGatewayConfigInvalidPostgres,
        SEGatewayConfigInvalidRest,
    ]
    FULL: ClassVar[Dict[str, JsonValue]] = {
        "schema_name": "gateway_two",
        "postgres": {"dsn_key": "SWARM_OTHER_DSN", "pool_max_size": 7},
        "rest": {"port": 9001},
    }
    UNKNOWN_KEY_CONFIGURATION: ClassVar[Dict[str, JsonValue]] = {"colour": "red"}
    BAD_DSN_KEY_CONFIGURATION: ClassVar[Dict[str, JsonValue]] = {"postgres": {"dsn_key": "lower"}}
    BAD_PORT_CONFIGURATION: ClassVar[Dict[str, JsonValue]] = {"rest": {"port": 0}}

    def test_defaults(self) -> None:
        config = GatewayConfig()
        assert config.schema_name == "gateway"
        assert config.postgres == PostgresConfig(dsn_key=GatewayConfig.DSN_KEY)
        assert config.rest == RestConfig()

    def test_full_valid_construction(self) -> None:
        config = GatewayConfig.model_validate(self.FULL)
        assert config.schema_name == "gateway_two"
        assert config.postgres == PostgresConfig(dsn_key="SWARM_OTHER_DSN", pool_max_size=7)
        assert config.rest == RestConfig(port=9001)

    @pytest.mark.parametrize("name", ["schema_name", "postgres", "rest"])
    def test_none_becomes_the_default(self, name: str) -> None:
        config = GatewayConfig.model_validate({name: None})
        default = GatewayConfig.model_fields[name].get_default(call_default_factory=True)
        assert getattr(config, name) == default

    @pytest.mark.parametrize(
        ("name", "value", "error"),
        [
            ("schema_name", "", SEGatewayConfigInvalidSchemaName),
            ("schema_name", "   ", SEGatewayConfigInvalidSchemaName),
            ("schema_name", 3, SEGatewayConfigInvalidSchemaName),
            ("schema_name", True, SEGatewayConfigInvalidSchemaName),
            ("schema_name", "Gateway", SEGatewayConfigInvalidSchemaName),
            ("schema_name", "1gateway", SEGatewayConfigInvalidSchemaName),
            ("schema_name", "gate-way", SEGatewayConfigInvalidSchemaName),
            ("schema_name", "gate way", SEGatewayConfigInvalidSchemaName),
            ("postgres", "SWARM_GATEWAY_POSTGRES_DSN", SEGatewayConfigInvalidPostgres),
            ("postgres", 3, SEGatewayConfigInvalidPostgres),
            ("postgres", [1], SEGatewayConfigInvalidPostgres),
            ("rest", "0.0.0.0", SEGatewayConfigInvalidRest),
            ("rest", 8000, SEGatewayConfigInvalidRest),
            ("rest", [1], SEGatewayConfigInvalidRest),
        ],
    )
    def test_rejects_bad_values(self, name: str, value: JsonValue, error: type[Exception]) -> None:
        with pytest.raises(error):
            GatewayConfig.model_validate({name: value})

    def test_rejects_unknown_keys(self) -> None:
        with pytest.raises(ValidationError):
            GatewayConfig.model_validate(self.UNKNOWN_KEY_CONFIGURATION)

    def test_round_trip(self) -> None:
        config = GatewayConfig.model_validate(self.FULL)
        assert GatewayConfig.model_validate(config.model_dump()) == config

    def test_a_nested_postgres_error_is_raised_unchanged(self) -> None:
        with pytest.raises(SEPostgresConfigInvalidDsnKey):
            GatewayConfig.model_validate(self.BAD_DSN_KEY_CONFIGURATION)

    def test_a_nested_rest_error_is_raised_unchanged(self) -> None:
        with pytest.raises(SERestConfigInvalidPort):
            GatewayConfig.model_validate(self.BAD_PORT_CONFIGURATION)

    @pytest.mark.parametrize("error", FIELD_ERRORS)
    def test_the_field_exceptions_share_the_model_base(self, error: type[Exception]) -> None:
        assert issubclass(error, SEInvalidGatewayConfigException)

    def test_the_unreadable_error_is_not_a_value_error(self) -> None:
        assert not issubclass(GatewayConfig.UNREADABLE, ValueError)

    def test_the_class_variables(self) -> None:
        assert issubclass(GatewayConfig, YamlCatalog)
        assert GatewayConfig.UNREADABLE is SEGatewayConfigUnreadable
        assert GatewayConfig.APP_FILE == "app.yaml"
        assert GatewayConfig.LOGGER_FILE == "logger.yaml"
        assert GatewayConfig.DSN_KEY == "SWARM_GATEWAY_POSTGRES_DSN"

    def test_the_app_root_entry_moves_the_conf_and_migrations_folders(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        monkeypatch.setenv(GatewayConfig.APP_ROOT_KEY, str(tmp_path))
        assert GatewayConfig.conf_folder() == tmp_path / GatewayConfig.CONF_FOLDER
        assert GatewayConfig.migrations_folder() == tmp_path / GatewayConfig.MIGRATIONS_FOLDER

    def test_the_app_folder_holds_the_conf_and_migrations_folders(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv(GatewayConfig.APP_ROOT_KEY, str(self.APP_FOLDER))
        assert GatewayConfig.conf_folder().is_dir()
        assert GatewayConfig.migrations_folder().is_dir()

    def test_app_yaml_writes_every_default_out(self) -> None:
        path = self.APP_FOLDER / GatewayConfig.CONF_FOLDER / GatewayConfig.APP_FILE
        assert GatewayConfig.load(path) == GatewayConfig()

    def test_an_unreadable_file_is_refused(self, tmp_path: Path) -> None:
        with pytest.raises(SEGatewayConfigUnreadable):
            GatewayConfig.load(tmp_path / "missing.yaml")
