from __future__ import annotations

from typing import ClassVar, Dict, List

import pytest
from pydantic import JsonValue, ValidationError

from simulator.models.config.exceptions import (
    SEFlightConfigInvalidArmTimeout,
    SEFlightConfigInvalidHeartbeatTimeout,
    SEFlightConfigInvalidRouteTimeout,
    SEFlightConfigInvalidStatusInterval,
)
from simulator.models.config.flight_config import FlightConfig


class TestFlightConfig:
    DEFAULTS: ClassVar[Dict[str, float]] = {
        "heartbeat_timeout_s": 30.0,
        "arm_timeout_s": 120.0,
        "route_timeout_s": 600.0,
        "status_interval_s": 5.0,
    }
    NAMES: ClassVar[List[str]] = list(DEFAULTS)
    ERRORS: ClassVar[Dict[str, type[Exception]]] = {
        "heartbeat_timeout_s": SEFlightConfigInvalidHeartbeatTimeout,
        "arm_timeout_s": SEFlightConfigInvalidArmTimeout,
        "route_timeout_s": SEFlightConfigInvalidRouteTimeout,
        "status_interval_s": SEFlightConfigInvalidStatusInterval,
    }
    BAD_VALUES: ClassVar[List[JsonValue]] = [0, -1.0, True, False, "5", [1]]
    UNKNOWN_KEY_CONFIGURATION: ClassVar[Dict[str, JsonValue]] = {"arm_timeout_s": 1.0, "colour": "red"}

    def test_defaults(self) -> None:
        config = FlightConfig()
        for name, default in self.DEFAULTS.items():
            assert getattr(config, name) == default

    def test_full_valid_construction(self) -> None:
        config = FlightConfig(heartbeat_timeout_s=1.5, arm_timeout_s=2.5, route_timeout_s=3.5, status_interval_s=0.5)
        assert config.heartbeat_timeout_s == 1.5
        assert config.arm_timeout_s == 2.5
        assert config.route_timeout_s == 3.5
        assert config.status_interval_s == 0.5

    @pytest.mark.parametrize("name", NAMES)
    def test_none_becomes_the_default(self, name: str) -> None:
        config = FlightConfig.model_validate({name: None})
        default = FlightConfig.model_fields[name].get_default(call_default_factory=True)
        assert getattr(config, name) == default

    @pytest.mark.parametrize("name", NAMES)
    @pytest.mark.parametrize("value", BAD_VALUES)
    def test_rejects_bad_values(self, name: str, value: JsonValue) -> None:
        with pytest.raises(self.ERRORS[name]):
            FlightConfig.model_validate({name: value})

    def test_rejects_unknown_keys(self) -> None:
        with pytest.raises(ValidationError):
            FlightConfig.model_validate(self.UNKNOWN_KEY_CONFIGURATION)

    @pytest.mark.parametrize("name", NAMES)
    def test_an_integer_is_accepted_as_a_number(self, name: str) -> None:
        assert getattr(FlightConfig.model_validate({name: 7}), name) == 7

    def test_round_trip(self) -> None:
        config = FlightConfig(heartbeat_timeout_s=4.0, route_timeout_s=90.0)
        data: Dict[str, JsonValue] = config.model_dump()
        assert FlightConfig.model_validate(data) == config
