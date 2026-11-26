from __future__ import annotations

# First-party imports
from swarm_models.config.simulator.exceptions.route_config.s_e_invalid_route_config_exception import (
    SEInvalidRouteConfigException,
)


class SERouteConfigInvalidAltitude(SEInvalidRouteConfigException):
    """Exception raised when an invalid ``altitude`` is provided."""
