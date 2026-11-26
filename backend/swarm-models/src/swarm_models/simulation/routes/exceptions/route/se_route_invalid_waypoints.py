from __future__ import annotations

# First-party imports
from swarm_models.simulation.routes.exceptions.route.se_invalid_route_exception import (
    SEInvalidRouteException,
)


class SERouteInvalidWaypoints(SEInvalidRouteException):
    """Exception raised when an invalid ``waypoints`` is provided."""
