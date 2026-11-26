from __future__ import annotations

# First-party imports
from swarm_models.config.simulator.exceptions.flight_config.s_e_invalid_flight_config_exception import (
    SEInvalidFlightConfigException,
)


class SEFlightConfigInvalidRouteTimeout(SEInvalidFlightConfigException):
    """Exception raised when an invalid ``route_timeout`` is provided."""
