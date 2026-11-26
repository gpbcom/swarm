from __future__ import annotations

# First-party imports
from simulator.models.routes.exceptions.waypoint.se_invalid_waypoint_exception import (
    SEInvalidWaypointException,
)


class SEWaypointInvalidLat(SEInvalidWaypointException):
    """Exception raised when an invalid ``lat_e7`` is provided."""
