from __future__ import annotations

# Standard library imports
from pathlib import Path
from typing import ClassVar, Dict, List

# Third-party imports
import pytest
import yaml
from pydantic import JsonValue, ValidationError

# First-party imports
from swarm_models.config.flight_engine.exceptions import (
    SEFlightEngineConfigInvalidDroneStatesCatalogPath,
    SEFlightEngineConfigInvalidLinkLostAfter,
    SEFlightEngineConfigInvalidLive,
    SEFlightEngineConfigInvalidMissionsCatalogPath,
    SEFlightEngineConfigInvalidNats,
    SEFlightEngineConfigInvalidStatusInterval,
    SEFlightEngineConfigInvalidTickInterval,
    SEFlightEngineConfigUnreadable,
    SEInvalidFlightEngineConfigException,
)
from swarm_models.config.flight_engine.flight_engine_config import FlightEngineConfig
from swarm_models.config.flight_engine.live_server_config import LiveServerConfig
from swarm_nats.models.config.nats_client_config import NatsClientConfig
from swarm_web.models.config.signals_config import SignalsConfig


class TestFlightEngineConfig:
    CONF_FOLDER: ClassVar[Path] = Path(__file__).resolve().parents[4] / "backend" / "apps" / "flight-engine" / "conf"
    APP_FILE: ClassVar[str] = "app.yaml"
    FIELDS: ClassVar[List[str]] = [
        "tick_interval_ms",
        "status_interval_s",
        "link_lost_after_ms",
        "missions_catalog_path",
        "drone_states_catalog_path",
        "nats",
        "live",
        "signals",
    ]
    FIELD_ERRORS: ClassVar[List[type[Exception]]] = [
        SEFlightEngineConfigInvalidTickInterval,
        SEFlightEngineConfigInvalidStatusInterval,
        SEFlightEngineConfigInvalidLinkLostAfter,
        SEFlightEngineConfigInvalidMissionsCatalogPath,
        SEFlightEngineConfigInvalidDroneStatesCatalogPath,
        SEFlightEngineConfigInvalidNats,
        SEFlightEngineConfigInvalidLive,
    ]
    UNKNOWN_KEY_CONFIGURATION: ClassVar[Dict[str, JsonValue]] = {"colour": "red"}
    FULL_CONFIGURATION: ClassVar[Dict[str, JsonValue]] = {
        "tick_interval_ms": 100,
        "status_interval_s": 2.5,
        "link_lost_after_ms": 3000,
        "missions_catalog_path": "other/missions.yaml",
        "drone_states_catalog_path": "other/drone_states.yaml",
        "nats": {"name": "engine"},
        "live": {"port": 9000},
    }

    def test_defaults(self) -> None:
        config = FlightEngineConfig()
        assert config.tick_interval_ms == 50
        assert config.status_interval_s == 5.0
        assert config.link_lost_after_ms == 5000
        assert config.missions_catalog_path == "conf/catalogs/missions.yaml"
        assert config.drone_states_catalog_path == "conf/catalogs/drone_states.yaml"
        assert config.nats == NatsClientConfig()
        assert config.live == LiveServerConfig()
        assert config.signals == SignalsConfig(service_name=FlightEngineConfig.SERVICE_NAME)

    def test_full_valid_construction(self) -> None:
        config = FlightEngineConfig.model_validate(self.FULL_CONFIGURATION)
        assert config.tick_interval_ms == 100
        assert config.status_interval_s == 2.5
        assert config.link_lost_after_ms == 3000
        assert config.missions_catalog_path == "other/missions.yaml"
        assert config.drone_states_catalog_path == "other/drone_states.yaml"
        assert config.nats == NatsClientConfig(name="engine")
        assert config.live == LiveServerConfig(port=9000)

    @pytest.mark.parametrize("name", FIELDS)
    def test_none_becomes_the_default(self, name: str) -> None:
        config = FlightEngineConfig.model_validate({name: None})
        default = FlightEngineConfig.model_fields[name].get_default(call_default_factory=True)
        assert getattr(config, name) == default

    @pytest.mark.parametrize(
        ("name", "value", "error"),
        [
            ("tick_interval_ms", 0, SEFlightEngineConfigInvalidTickInterval),
            ("tick_interval_ms", -50, SEFlightEngineConfigInvalidTickInterval),
            ("tick_interval_ms", True, SEFlightEngineConfigInvalidTickInterval),
            ("tick_interval_ms", 1.5, SEFlightEngineConfigInvalidTickInterval),
            ("tick_interval_ms", "50", SEFlightEngineConfigInvalidTickInterval),
            ("status_interval_s", 0, SEFlightEngineConfigInvalidStatusInterval),
            ("status_interval_s", -1.0, SEFlightEngineConfigInvalidStatusInterval),
            ("status_interval_s", True, SEFlightEngineConfigInvalidStatusInterval),
            ("status_interval_s", "5", SEFlightEngineConfigInvalidStatusInterval),
            ("link_lost_after_ms", 0, SEFlightEngineConfigInvalidLinkLostAfter),
            ("link_lost_after_ms", -1, SEFlightEngineConfigInvalidLinkLostAfter),
            ("link_lost_after_ms", True, SEFlightEngineConfigInvalidLinkLostAfter),
            ("link_lost_after_ms", 2.5, SEFlightEngineConfigInvalidLinkLostAfter),
            ("missions_catalog_path", "", SEFlightEngineConfigInvalidMissionsCatalogPath),
            ("missions_catalog_path", "   ", SEFlightEngineConfigInvalidMissionsCatalogPath),
            ("missions_catalog_path", 3, SEFlightEngineConfigInvalidMissionsCatalogPath),
            ("missions_catalog_path", True, SEFlightEngineConfigInvalidMissionsCatalogPath),
            ("drone_states_catalog_path", "", SEFlightEngineConfigInvalidDroneStatesCatalogPath),
            ("drone_states_catalog_path", 3, SEFlightEngineConfigInvalidDroneStatesCatalogPath),
            ("drone_states_catalog_path", True, SEFlightEngineConfigInvalidDroneStatesCatalogPath),
            ("nats", 3, SEFlightEngineConfigInvalidNats),
            ("nats", "nats", SEFlightEngineConfigInvalidNats),
            ("nats", ["nats"], SEFlightEngineConfigInvalidNats),
            ("live", 3, SEFlightEngineConfigInvalidLive),
            ("live", "live", SEFlightEngineConfigInvalidLive),
            ("live", ["live"], SEFlightEngineConfigInvalidLive),
        ],
    )
    def test_rejects_bad_values(self, name: str, value: JsonValue, error: type[Exception]) -> None:
        with pytest.raises(error):
            FlightEngineConfig.model_validate({name: value})

    def test_rejects_unknown_keys(self) -> None:
        with pytest.raises(ValidationError):
            FlightEngineConfig.model_validate(self.UNKNOWN_KEY_CONFIGURATION)

    def test_round_trip(self) -> None:
        config = FlightEngineConfig.model_validate(self.FULL_CONFIGURATION)
        data: Dict[str, JsonValue] = config.model_dump()
        assert FlightEngineConfig.model_validate(data) == config

    @pytest.mark.parametrize("error", FIELD_ERRORS)
    def test_the_field_exceptions_share_the_model_base(self, error: type[Exception]) -> None:
        assert issubclass(error, SEInvalidFlightEngineConfigException)

    def test_a_catalog_path_with_surrounding_spaces_is_stripped(self) -> None:
        assert FlightEngineConfig(missions_catalog_path="  a.yaml  ").missions_catalog_path == "a.yaml"

    def test_the_unreadable_error_is_the_one_of_load(self) -> None:
        assert FlightEngineConfig.UNREADABLE is SEFlightEngineConfigUnreadable

    def test_a_missing_file_is_unreadable(self, tmp_path: Path) -> None:
        with pytest.raises(SEFlightEngineConfigUnreadable):
            FlightEngineConfig.load(tmp_path / self.APP_FILE)

    def test_the_app_file_loads_into_the_defaults(self) -> None:
        assert FlightEngineConfig.load(self.CONF_FOLDER / self.APP_FILE) == FlightEngineConfig()

    def test_the_app_file_writes_every_default_out(self) -> None:
        written = yaml.safe_load((self.CONF_FOLDER / self.APP_FILE).read_text(encoding="utf-8"))
        assert set(written) == set(self.FIELDS)
        assert set(written["nats"]) == set(NatsClientConfig.model_fields)
        assert set(written["live"]) == set(LiveServerConfig.model_fields)
        assert set(written["signals"]) == set(SignalsConfig.model_fields)

    def test_a_signals_mapping_is_read_from_yaml(self, tmp_path: Path) -> None:
        path = tmp_path / "app.yaml"
        path.write_text(yaml.safe_dump({"signals": {"enabled": True, "cell": "eu_west"}}), encoding="utf-8")
        assert FlightEngineConfig.load(path).signals == SignalsConfig(enabled=True, cell="eu_west")
