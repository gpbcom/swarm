from __future__ import annotations

from swarm_models.telemetry.exceptions.squad_frame import (
    SEInvalidSquadFrameException,
    SESquadFrameDuplicateDrone,
    SESquadFrameInvalidFrames,
    SESquadFrameInvalidMissionId,
    SESquadFrameInvalidTraceParent,
    SESquadFrameInvalidTUs,
    SESquadFrameMissionMismatch,
)
from swarm_models.telemetry.exceptions.telemetry_frame import (
    SEInvalidTelemetryFrameException,
    SETelemetryFrameInvalidAltitudeM,
    SETelemetryFrameInvalidBatteryPct,
    SETelemetryFrameInvalidDroneId,
    SETelemetryFrameInvalidHeadingDeg,
    SETelemetryFrameInvalidLatE7,
    SETelemetryFrameInvalidLinkQualityPct,
    SETelemetryFrameInvalidLonE7,
    SETelemetryFrameInvalidMissionId,
    SETelemetryFrameInvalidSeq,
    SETelemetryFrameInvalidSpeedMS,
    SETelemetryFrameInvalidState,
    SETelemetryFrameInvalidTUs,
)

__all__ = [
    "SEInvalidSquadFrameException",
    "SEInvalidTelemetryFrameException",
    "SESquadFrameDuplicateDrone",
    "SESquadFrameInvalidFrames",
    "SESquadFrameInvalidMissionId",
    "SESquadFrameInvalidTUs",
    "SESquadFrameInvalidTraceParent",
    "SESquadFrameMissionMismatch",
    "SETelemetryFrameInvalidAltitudeM",
    "SETelemetryFrameInvalidBatteryPct",
    "SETelemetryFrameInvalidDroneId",
    "SETelemetryFrameInvalidHeadingDeg",
    "SETelemetryFrameInvalidLatE7",
    "SETelemetryFrameInvalidLinkQualityPct",
    "SETelemetryFrameInvalidLonE7",
    "SETelemetryFrameInvalidMissionId",
    "SETelemetryFrameInvalidSeq",
    "SETelemetryFrameInvalidSpeedMS",
    "SETelemetryFrameInvalidState",
    "SETelemetryFrameInvalidTUs",
]
