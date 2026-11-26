from __future__ import annotations

# First-party imports
from swarm_models.flight.telemetry.exceptions.drone_sample.se_invalid_drone_sample_exception import (
    SEInvalidDroneSampleException,
)


class SEDroneSampleInvalidLatE7(SEInvalidDroneSampleException):
    """Exception raised when an invalid ``lat_e7`` is provided."""
