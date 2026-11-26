from __future__ import annotations

# First-party imports
from flight_engine.models.telemetry.exceptions.drone_sample.se_invalid_drone_sample_exception import (
    SEInvalidDroneSampleException,
)


class SEDroneSampleInvalidHdgCdeg(SEInvalidDroneSampleException):
    """Exception raised when an invalid ``hdg_cdeg`` is provided."""
