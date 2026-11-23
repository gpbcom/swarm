from __future__ import annotations

# Standard library imports
import math
from itertools import pairwise
from typing import ClassVar, List, Tuple

# Third-party imports
import pytest

# First-party imports
from simulator.models.config.route_config import RouteConfig
from simulator.models.routes.route import Route
from simulator.models.routes.waypoint import Waypoint
from simulator.service.routes.square_route_builder import SquareRouteBuilder


class TestSquareRouteBuilder:
    E7: ClassVar[float] = 1e7
    EARTH_RADIUS_M: ClassVar[float] = 6371000.0
    TOLERANCE: ClassVar[float] = 0.005
    START_POINTS: ClassVar[List[Tuple[int, int]]] = [
        (473977420, 85455940),
        (0, 0),
        (-337688470, 1512093000),
        (-540000000, -683000000),
        (473977420, 1799990000),
        (473977420, -1799990000),
    ]

    def haversine_m(self, a: Waypoint, b: Waypoint) -> float:
        lat_a = math.radians(a.lat_e7 / self.E7)
        lat_b = math.radians(b.lat_e7 / self.E7)
        d_lat = lat_b - lat_a
        d_lon = math.radians((b.lon_e7 - a.lon_e7) / self.E7)
        h = math.sin(d_lat / 2) ** 2 + math.cos(lat_a) * math.cos(lat_b) * math.sin(d_lon / 2) ** 2
        return 2 * self.EARTH_RADIUS_M * math.asin(math.sqrt(h))

    def build(self, lat_e7: int, lon_e7: int, side_m: float = 50.0, altitude_m: float = 20.0) -> Route:
        builder = SquareRouteBuilder(RouteConfig(side_m=side_m, altitude_m=altitude_m))
        return builder.build(lat_e7, lon_e7)

    def test_the_route_has_five_waypoints_and_ends_where_it_starts(self) -> None:
        route = self.build(*self.START_POINTS[0])
        assert len(route.waypoints) == 5
        assert route.waypoints[-1] == route.waypoints[0]

    def test_the_first_corner_is_the_start(self) -> None:
        lat_e7, lon_e7 = self.START_POINTS[0]
        first = self.build(lat_e7, lon_e7).waypoints[0]
        assert (first.lat_e7, first.lon_e7) == (lat_e7, lon_e7)

    @pytest.mark.parametrize("lat_e7, lon_e7", START_POINTS)
    def test_b_is_north_of_a_and_d_is_east_of_a(self, lat_e7: int, lon_e7: int) -> None:
        a, b, c, d, _ = self.build(lat_e7, lon_e7).waypoints
        assert b.lat_e7 > a.lat_e7
        assert b.lon_e7 == a.lon_e7
        assert d.lat_e7 == a.lat_e7
        assert d.lon_e7 > a.lon_e7
        assert c.lat_e7 == b.lat_e7
        assert c.lon_e7 == d.lon_e7

    @pytest.mark.parametrize("lat_e7, lon_e7", START_POINTS)
    @pytest.mark.parametrize("side_m", [50.0, 20.0, 200.0])
    def test_every_side_measures_side_m(self, lat_e7: int, lon_e7: int, side_m: float) -> None:
        points = self.build(lat_e7, lon_e7, side_m=side_m).waypoints
        for start, end in pairwise(points):
            assert self.haversine_m(start, end) == pytest.approx(side_m, rel=self.TOLERANCE)

    @pytest.mark.parametrize("lat_e7, lon_e7", START_POINTS)
    def test_the_diagonal_is_side_m_times_root_two(self, lat_e7: int, lon_e7: int) -> None:
        a, _, c, _, _ = self.build(lat_e7, lon_e7, side_m=100.0).waypoints
        assert self.haversine_m(a, c) == pytest.approx(100.0 * math.sqrt(2), rel=self.TOLERANCE)

    def test_every_altitude_is_the_configured_default(self) -> None:
        route = self.build(*self.START_POINTS[0])
        assert {point.altitude_m for point in route.waypoints} == {20.0}

    def test_a_custom_side_and_altitude_are_used(self) -> None:
        lat_e7, lon_e7 = self.START_POINTS[0]
        route = self.build(lat_e7, lon_e7, side_m=120.0, altitude_m=35.5)
        assert {point.altitude_m for point in route.waypoints} == {35.5}
        assert self.haversine_m(route.waypoints[0], route.waypoints[1]) == pytest.approx(120.0, rel=self.TOLERANCE)

    def test_the_default_configuration_gives_a_fifty_metre_square(self) -> None:
        lat_e7, lon_e7 = self.START_POINTS[0]
        route = SquareRouteBuilder(RouteConfig()).build(lat_e7, lon_e7)
        assert self.haversine_m(route.waypoints[0], route.waypoints[1]) == pytest.approx(50.0, rel=self.TOLERANCE)
        assert {point.altitude_m for point in route.waypoints} == {20.0}
