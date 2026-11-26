from __future__ import annotations

# Standard library imports
from typing import ClassVar, Dict, List

# Third-party imports
import pytest
from pydantic import JsonValue, ValidationError

# First-party imports
from swarm_models.simulation.routes.exceptions import SERouteInvalidWaypoints
from swarm_models.simulation.routes.route import Route
from swarm_models.simulation.routes.waypoint import Waypoint


class TestRoute:
    FIRST: ClassVar[Dict[str, JsonValue]] = {"lat_e7": 487000000, "lon_e7": 23000000, "altitude_m": 30.0}
    SECOND: ClassVar[Dict[str, JsonValue]] = {"lat_e7": 487100000, "lon_e7": 23100000, "altitude_m": 40.0}
    WAYPOINTS_KEY: ClassVar[str] = "waypoints"

    def build(self, **changes: JsonValue) -> Route:
        values: Dict[str, JsonValue] = {self.WAYPOINTS_KEY: [self.FIRST, self.SECOND]}
        values.update(changes)
        return Route.model_validate(values)

    def test_defaults(self) -> None:
        assert Route.WAYPOINTS_MIN == 2
        with pytest.raises(ValidationError):
            Route.model_validate({})

    def test_full_valid_construction(self) -> None:
        waypoints: List[Waypoint] = [Waypoint.model_validate(self.FIRST), Waypoint.model_validate(self.SECOND)]
        route = Route(waypoints=waypoints)
        assert route.waypoints == waypoints

    def test_none_is_refused_as_the_waypoints_have_no_default(self) -> None:
        with pytest.raises(SERouteInvalidWaypoints):
            self.build(waypoints=None)

    @pytest.mark.parametrize("value", [[], [FIRST], "waypoints", 3, True, [3, 4]])
    def test_rejects_bad_values(self, value: JsonValue) -> None:
        with pytest.raises(SERouteInvalidWaypoints):
            self.build(waypoints=value)

    def test_a_mapping_waypoint_becomes_a_waypoint(self) -> None:
        assert isinstance(self.build().waypoints[0], Waypoint)

    def test_exactly_the_minimum_of_waypoints_is_accepted(self) -> None:
        assert len(self.build().waypoints) == Route.WAYPOINTS_MIN

    def test_rejects_unknown_keys(self) -> None:
        with pytest.raises(ValidationError):
            self.build(extra=1)

    def test_assigning_a_field_of_a_built_route_is_refused(self) -> None:
        route = self.build()
        with pytest.raises(ValidationError):
            route.waypoints = []

    def test_round_trip(self) -> None:
        route = self.build()
        assert Route.model_validate(route.model_dump()) == route
        assert Route.model_validate_json(route.model_dump_json()) == route
