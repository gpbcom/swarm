from __future__ import annotations

# Standard library imports
from typing import ClassVar, Dict

# Third-party imports
import pytest
from pydantic import JsonValue, ValidationError

# First-party imports
from swarm_models.config.flight_engine.exceptions import (
    SEInvalidLiveServerConfigException,
    SELiveServerConfigInvalidHost,
    SELiveServerConfigInvalidPort,
    SELiveServerConfigInvalidStatusInterval,
)
from swarm_models.config.flight_engine.live_server_config import LiveServerConfig


class TestLiveServerConfig:
    FULL_CONFIGURATION: ClassVar[Dict[str, JsonValue]] = {"host": "0.0.0.0", "port": 9000, "status_interval_s": 2.5}
    UNKNOWN_KEY_CONFIGURATION: ClassVar[Dict[str, JsonValue]] = {"colour": "red"}

    def test_defaults(self) -> None:
        config = LiveServerConfig()
        assert config.host == "127.0.0.1"
        assert config.port == 8080
        assert config.status_interval_s == 5.0

    def test_full_valid_construction(self) -> None:
        config = LiveServerConfig.model_validate(self.FULL_CONFIGURATION)
        assert config.host == "0.0.0.0"
        assert config.port == 9000
        assert config.status_interval_s == 2.5

    @pytest.mark.parametrize("name", ["host", "port", "status_interval_s"])
    def test_none_becomes_the_default(self, name: str) -> None:
        config = LiveServerConfig.model_validate({name: None})
        default = LiveServerConfig.model_fields[name].get_default(call_default_factory=True)
        assert getattr(config, name) == default

    @pytest.mark.parametrize(
        ("name", "value", "error"),
        [
            ("host", "", SELiveServerConfigInvalidHost),
            ("host", "   ", SELiveServerConfigInvalidHost),
            ("host", 3, SELiveServerConfigInvalidHost),
            ("host", True, SELiveServerConfigInvalidHost),
            ("port", 0, SELiveServerConfigInvalidPort),
            ("port", 65536, SELiveServerConfigInvalidPort),
            ("port", -1, SELiveServerConfigInvalidPort),
            ("port", True, SELiveServerConfigInvalidPort),
            ("port", 1.5, SELiveServerConfigInvalidPort),
            ("port", "80", SELiveServerConfigInvalidPort),
            ("status_interval_s", 0, SELiveServerConfigInvalidStatusInterval),
            ("status_interval_s", -1.0, SELiveServerConfigInvalidStatusInterval),
            ("status_interval_s", True, SELiveServerConfigInvalidStatusInterval),
            ("status_interval_s", "5", SELiveServerConfigInvalidStatusInterval),
        ],
    )
    def test_rejects_bad_values(self, name: str, value: JsonValue, error: type[Exception]) -> None:
        with pytest.raises(error):
            LiveServerConfig.model_validate({name: value})

    def test_rejects_unknown_keys(self) -> None:
        with pytest.raises(ValidationError):
            LiveServerConfig.model_validate(self.UNKNOWN_KEY_CONFIGURATION)

    def test_round_trip(self) -> None:
        config = LiveServerConfig.model_validate(self.FULL_CONFIGURATION)
        assert LiveServerConfig.model_validate(config.model_dump()) == config

    @pytest.mark.parametrize("port", [1, 65535])
    def test_the_bounds_of_the_port_are_accepted(self, port: int) -> None:
        assert LiveServerConfig(port=port).port == port

    def test_a_host_with_surrounding_spaces_is_stripped(self) -> None:
        assert LiveServerConfig(host="  localhost  ").host == "localhost"

    @pytest.mark.parametrize(
        "error",
        [SELiveServerConfigInvalidHost, SELiveServerConfigInvalidPort, SELiveServerConfigInvalidStatusInterval],
    )
    def test_the_field_exceptions_share_the_model_base(self, error: type[Exception]) -> None:
        assert issubclass(error, SEInvalidLiveServerConfigException)
