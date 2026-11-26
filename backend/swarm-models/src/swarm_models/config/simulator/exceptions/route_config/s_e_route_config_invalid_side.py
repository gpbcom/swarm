from __future__ import annotations

# First-party imports
from simulator.models.config.exceptions.route_config.s_e_invalid_route_config_exception import (
    SEInvalidRouteConfigException,
)


class SERouteConfigInvalidSide(SEInvalidRouteConfigException):
    """Exception raised when an invalid ``side`` is provided."""
