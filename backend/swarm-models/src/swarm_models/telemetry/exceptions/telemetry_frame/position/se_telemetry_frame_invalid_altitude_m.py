from __future__ import annotations

# First-party imports
from swarm_models.models.telemetry.exceptions.telemetry_frame.se_invalid_telemetry_frame_exception import (
    SEInvalidTelemetryFrameException,
)


class SETelemetryFrameInvalidAltitudeM(SEInvalidTelemetryFrameException):
    """Exception raised when an invalid ``altitude_m`` is provided."""
