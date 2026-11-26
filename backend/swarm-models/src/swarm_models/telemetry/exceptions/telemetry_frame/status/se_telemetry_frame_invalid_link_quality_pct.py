from __future__ import annotations

# First-party imports
from swarm_models.models.telemetry.exceptions.telemetry_frame.se_invalid_telemetry_frame_exception import (
    SEInvalidTelemetryFrameException,
)


class SETelemetryFrameInvalidLinkQualityPct(SEInvalidTelemetryFrameException):
    """Exception raised when an invalid ``link_quality_pct`` is provided."""
