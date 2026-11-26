from __future__ import annotations

# First-party imports
from swarm_models.telemetry.exceptions.telemetry_frame.se_invalid_telemetry_frame_exception import (
    SEInvalidTelemetryFrameException,
)


class SETelemetryFrameInvalidHeadingDeg(SEInvalidTelemetryFrameException):
    """Exception raised when an invalid ``heading_deg`` is provided."""
