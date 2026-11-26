from __future__ import annotations

# First-party imports
from swarm_models.config.flight_engine.exceptions.flight_engine_config.se_invalid_flight_engine_config_exception import (
    SEInvalidFlightEngineConfigException,
)


class SEFlightEngineConfigInvalidStatusInterval(SEInvalidFlightEngineConfigException):
    """Exception raised when an invalid ``status_interval_s`` is provided."""
