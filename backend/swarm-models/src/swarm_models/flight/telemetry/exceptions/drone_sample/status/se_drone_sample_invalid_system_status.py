from __future__ import annotations

# First-party imports
from swarm_models.flight.telemetry.exceptions.drone_sample.se_invalid_drone_sample_exception import (
    SEInvalidDroneSampleException,
)


class SEDroneSampleInvalidSystemStatus(SEInvalidDroneSampleException):
    """Exception raised when an invalid ``system_status`` is provided."""
