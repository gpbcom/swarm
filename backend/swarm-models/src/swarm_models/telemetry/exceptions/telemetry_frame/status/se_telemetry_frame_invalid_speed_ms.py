from __future__ import annotations

# First-party imports
from swarm_models.telemetry.exceptions.telemetry_frame.se_invalid_telemetry_frame_exception import (
    SEInvalidTelemetryFrameException,
)


class SETelemetryFrameInvalidSpeedMS(SEInvalidTelemetryFrameException):
    """Exception raised when an invalid ``speed_m_s`` is provided."""
