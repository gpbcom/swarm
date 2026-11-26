from __future__ import annotations

# Standard library imports
from typing import ClassVar, Dict

# Third-party imports
import pytest
from pydantic import JsonValue, ValidationError

# First-party imports
from simulator.models.routes.exceptions import (
    SEWaypointInvalidAltitude,
    SEWaypointInvalidLat,
    SEWaypointInvalidLon,
)
from simulator.models.routes.waypoint import Waypoint


class TestWaypoint:
    VALID: ClassVar[Dict[str, JsonValue]] = {"lat_e7": 487000000, "lon_e7": 23000000, "altitude_m": 30.5}

    def build(self, **changes: JsonValue) -> Waypoint:
        values: Dict[str, JsonValue] = dict(self.VALID)
        values.update(changes)
        return Waypoint.model_validate(values)

    def test_defaults(self) -> None:
        with pytest.raises(ValidationError):
            Waypoint.model_validate({})

    def test_full_valid_construction(self) -> None:
        waypoint = Waypoint(lat_e7=487000000, lon_e7=23000000, altitude_m=30.5)
        assert waypoint.lat_e7 == 487000000
        assert waypoint.lon_e7 == 23000000
        assert waypoint.altitude_m == 30.5

    @pytest.mark.parametrize(
        ("name", "error"),
        [
            ("lat_e7", SEWaypointInvalidLat),
            ("lon_e7", SEWaypointInvalidLon),
            ("altitude_m", SEWaypointInvalidAltitude),
        ],
    )
    def test_none_is_refused_as_no_field_has_a_default(self, name: str, error: type[Exception]) -> None:
        with pytest.raises(error):
            self.build(**{name: None})

    @pytest.mark.parametrize(
        ("name", "value", "error"),
        [
            ("lat_e7", 900000001, SEWaypointInvalidLat),
            ("lat_e7", -900000001, SEWaypointInvalidLat),
            ("lat_e7", True, SEWaypointInvalidLat),
            ("lat_e7", 1.5, SEWaypointInvalidLat),
            ("lat_e7", "1", SEWaypointInvalidLat),
            ("lon_e7", 1800000001, SEWaypointInvalidLon),
            ("lon_e7", -1800000001, SEWaypointInvalidLon),
            ("lon_e7", True, SEWaypointInvalidLon),
            ("lon_e7", 1.5, SEWaypointInvalidLon),
            ("lon_e7", "1", SEWaypointInvalidLon),
            ("altitude_m", 0, SEWaypointInvalidAltitude),
            ("altitude_m", -1.0, SEWaypointInvalidAltitude),
            ("altitude_m", float("nan"), SEWaypointInvalidAltitude),
            ("altitude_m", float("inf"), SEWaypointInvalidAltitude),
            ("altitude_m", True, SEWaypointInvalidAltitude),
            ("altitude_m", "30", SEWaypointInvalidAltitude),
        ],
    )
    def test_rejects_bad_values(self, name: str, value: JsonValue, error: type[Exception]) -> None:
        with pytest.raises(error):
            self.build(**{name: value})

    @pytest.mark.parametrize(
        ("name", "value"),
        [
            ("lat_e7", 900000000),
            ("lat_e7", -900000000),
            ("lon_e7", 1800000000),
            ("lon_e7", -1800000000),
        ],
    )
    def test_the_bounds_are_accepted(self, name: str, value: int) -> None:
        assert getattr(self.build(**{name: value}), name) == value

    def test_an_integer_altitude_is_accepted(self) -> None:
        assert self.build(altitude_m=10).altitude_m == 10.0

    def test_rejects_unknown_keys(self) -> None:
        with pytest.raises(ValidationError):
            self.build(extra=1)

    def test_assigning_a_field_of_a_built_waypoint_is_refused(self) -> None:
        waypoint = self.build()
        with pytest.raises(ValidationError):
            waypoint.lat_e7 = 1

    def test_round_trip(self) -> None:
        waypoint = self.build()
        assert Waypoint.model_validate(waypoint.model_dump()) == waypoint
        assert Waypoint.model_validate_json(waypoint.model_dump_json()) == waypoint
