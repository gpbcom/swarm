from __future__ import annotations

# First-party imports
from flight_engine.models.config.exceptions.flight_engine_config.se_invalid_flight_engine_config_exception import (
    SEInvalidFlightEngineConfigException,
)


class SEFlightEngineConfigInvalidNats(SEInvalidFlightEngineConfigException):
    """Exception raised when an invalid ``nats`` is provided."""
