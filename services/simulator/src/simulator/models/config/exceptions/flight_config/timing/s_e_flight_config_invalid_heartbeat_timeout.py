from __future__ import annotations

# First-party imports
from simulator.models.config.exceptions.flight_config.s_e_invalid_flight_config_exception import (
    SEInvalidFlightConfigException,
)


class SEFlightConfigInvalidHeartbeatTimeout(SEInvalidFlightConfigException):
    """Exception raised when an invalid ``heartbeat_timeout`` is provided."""
