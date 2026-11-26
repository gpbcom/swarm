from __future__ import annotations

# First-party imports
from flight_engine.models.telemetry.exceptions.drone_sample.se_invalid_drone_sample_exception import (
    SEInvalidDroneSampleException,
)


class SEDroneSampleInvalidVyCmS(SEInvalidDroneSampleException):
    """Exception raised when an invalid ``vy_cm_s`` is provided."""
