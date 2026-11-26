from __future__ import annotations

# Standard library imports
import math
from logging import Logger, getLogger
from typing import ClassVar, List, Optional

# First-party imports
from simulator.models.config.route_config import RouteConfig
from simulator.models.routes.route import Route
from simulator.models.routes.waypoint import Waypoint


class SquareRouteBuilder:
    """Build the square route a simulated drone flies from its start point.

    Attributes:
        EARTH_RADIUS_M (float): The mean radius of the Earth, in metres.
        E7 (float): The factor between degrees and the integer e7 coordinates.
        LON_E7_SPAN (int): The width of the longitude range, in e7 degrees, used to wrap past the antimeridian.
        config (RouteConfig): The side and the altitude of the square.
        logger (Logger): Logger instance.

    Notes:
        - The square runs A, A+north, A+north+east, A+east, then back to A.
        - **The east offset is scaled by the cosine of the start latitude, so every side measures ``side_m``.**
        - A longitude that would pass the antimeridian wraps to the other hemisphere.
    """

    EARTH_RADIUS_M: ClassVar[float] = 6371000.0
    E7: ClassVar[float] = 1e7
    LON_E7_SPAN: ClassVar[int] = Waypoint.LON_E7_MAX - Waypoint.LON_E7_MIN

    def __init__(self, config: RouteConfig, logger: Optional[Logger] = None) -> None:
        """Create the builder.

        Args:
            config (RouteConfig): The side and the altitude of the square.
            logger (Optional[Logger]): Logger instance.
        """
        self.config = config
        self.logger = logger if logger else getLogger(__name__)

    ############################
    # Internal Helpers Methods #
    ############################

    def _wrap_lon_e7(self, lon_e7: int) -> int:
        """Bring a longitude back into its bounds.

        Args:
            lon_e7 (int): The longitude, in e7 degrees.

        Returns:
            int: The same longitude, within the bounds of a waypoint.
        """
        if lon_e7 > Waypoint.LON_E7_MAX:
            self.logger.debug("Longitude %d passes the antimeridian, wrapping it.", lon_e7)
            return lon_e7 - self.LON_E7_SPAN
        self.logger.debug("Longitude %d is within its bounds.", lon_e7)
        return lon_e7

    ############################
    # Publicly Exposed Methods #
    ############################

    def build(self, lat_e7: int, lon_e7: int) -> Route:
        """Build the square route starting at one point.

        Args:
            lat_e7 (int): The latitude of the start, in e7 degrees.
            lon_e7 (int): The longitude of the start, in e7 degrees.

        Returns:
            Route: Five waypoints, A, A+north, A+north+east, A+east and A again.
        """
        d_lat_e7 = round(math.degrees(self.config.side_m / self.EARTH_RADIUS_M) * self.E7)
        cos_lat = math.cos(math.radians(lat_e7 / self.E7))
        d_lon_e7 = round(math.degrees(self.config.side_m / (self.EARTH_RADIUS_M * cos_lat)) * self.E7)
        east_lon_e7 = self._wrap_lon_e7(lon_e7 + d_lon_e7)
        altitude_m = self.config.altitude_m
        corner_a = Waypoint(lat_e7=lat_e7, lon_e7=lon_e7, altitude_m=altitude_m)
        corner_b = Waypoint(lat_e7=lat_e7 + d_lat_e7, lon_e7=lon_e7, altitude_m=altitude_m)
        corner_c = Waypoint(lat_e7=lat_e7 + d_lat_e7, lon_e7=east_lon_e7, altitude_m=altitude_m)
        corner_d = Waypoint(lat_e7=lat_e7, lon_e7=east_lon_e7, altitude_m=altitude_m)
        waypoints: List[Waypoint] = [corner_a, corner_b, corner_c, corner_d, corner_a]
        route = Route(waypoints=waypoints)
        self.logger.debug(
            "Built a square route of %.1f m at %.1f m from %d, %d.", self.config.side_m, altitude_m, lat_e7, lon_e7
        )
        return route
