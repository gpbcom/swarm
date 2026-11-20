from __future__ import annotations

from typing import ClassVar, Dict

import pytest
from pydantic import JsonValue, ValidationError

from simulator.models.config.exceptions import SERouteConfigInvalidAltitude, SERouteConfigInvalidSide
from simulator.models.config.route_config import RouteConfig


class TestRouteConfig:
    UNKNOWN_KEY_CONFIGURATION: ClassVar[Dict[str, JsonValue]] = {"side_m": 10.0, "colour": "red"}

    def test_defaults(self) -> None:
        config = RouteConfig()
        assert config.side_m == 50.0
        assert config.altitude_m == 20.0

    def test_full_valid_construction(self) -> None:
        config = RouteConfig(side_m=80.0, altitude_m=35.5)
        assert config.side_m == 80.0
        assert config.altitude_m == 35.5

    @pytest.mark.parametrize("name", ["side_m", "altitude_m"])
    def test_none_becomes_the_default(self, name: str) -> None:
        config = RouteConfig.model_validate({name: None})
        default = RouteConfig.model_fields[name].get_default(call_default_factory=True)
        assert getattr(config, name) == default

    @pytest.mark.parametrize(
        ("name", "value", "error"),
        [
            ("side_m", 0, SERouteConfigInvalidSide),
            ("side_m", -1.0, SERouteConfigInvalidSide),
            ("side_m", True, SERouteConfigInvalidSide),
            ("side_m", "50", SERouteConfigInvalidSide),
            ("altitude_m", 0, SERouteConfigInvalidAltitude),
            ("altitude_m", -1.0, SERouteConfigInvalidAltitude),
            ("altitude_m", True, SERouteConfigInvalidAltitude),
            ("altitude_m", "20", SERouteConfigInvalidAltitude),
        ],
    )
    def test_rejects_bad_values(self, name: str, value: JsonValue, error: type[Exception]) -> None:
        with pytest.raises(error):
            RouteConfig.model_validate({name: value})

    def test_rejects_unknown_keys(self) -> None:
        with pytest.raises(ValidationError):
            RouteConfig.model_validate(self.UNKNOWN_KEY_CONFIGURATION)

    def test_an_integer_is_accepted_as_a_number(self) -> None:
        assert RouteConfig(side_m=10).side_m == 10

    def test_round_trip(self) -> None:
        config = RouteConfig(side_m=12.5, altitude_m=7.0)
        data: Dict[str, JsonValue] = config.model_dump()
        assert RouteConfig.model_validate(data) == config
