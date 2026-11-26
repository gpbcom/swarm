from __future__ import annotations

# First-party imports
from simulator.models.config.exceptions.flight_config.s_e_invalid_flight_config_exception import (
    SEInvalidFlightConfigException,
)


class SEFlightConfigInvalidArmTimeout(SEInvalidFlightConfigException):
    """Exception raised when an invalid ``arm_timeout`` is provided."""
