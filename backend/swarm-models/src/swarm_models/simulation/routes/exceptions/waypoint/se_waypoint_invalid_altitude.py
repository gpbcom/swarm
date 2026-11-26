from __future__ import annotations

# First-party imports
from swarm_models.simulation.routes.exceptions.waypoint.se_invalid_waypoint_exception import (
    SEInvalidWaypointException,
)


class SEWaypointInvalidAltitude(SEInvalidWaypointException):
    """Exception raised when an invalid ``altitude_m`` is provided."""
