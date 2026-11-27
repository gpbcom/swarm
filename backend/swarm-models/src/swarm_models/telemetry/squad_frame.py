from __future__ import annotations

# Standard library imports
import re
from typing import ClassVar, List, Optional, Set
from uuid import UUID

# Third-party imports
from pydantic import ConfigDict, Field, JsonValue, field_validator, model_validator

# First-party imports
from swarm_models.base.swarm_model import SwarmModel
from swarm_models.telemetry.exceptions import (
    SESquadFrameDuplicateDrone,
    SESquadFrameInvalidFrames,
    SESquadFrameInvalidMissionId,
    SESquadFrameInvalidTraceParent,
    SESquadFrameInvalidTUs,
    SESquadFrameMissionMismatch,
)
from swarm_models.telemetry.telemetry_frame import TelemetryFrame


class SquadFrame(SwarmModel):
    """The frames of every Drone of one Mission at one tick.

    Attributes:
        model_config (ConfigDict): Forbids unknown keys and freezes the squad frame.
        mission_id (UUID): The Mission of the frames.
        t_us (int): The moment of the tick, in microseconds since the epoch.
        frames (List[TelemetryFrame]): One frame per Drone.
        trace_parent (Optional[str]): The W3C trace parent of the tick that built the frame.
        T_US_MIN (ClassVar[int]): The smallest accepted ``t_us``.
        TRACE_PARENT_PATTERN (ClassVar[str]): The W3C ``traceparent`` format, in lower case.
        TRACE_ID_ZEROS (ClassVar[str]): The all-zero trace id, which is invalid.
        SPAN_ID_ZEROS (ClassVar[str]): The all-zero span id, which is invalid.

    Notes:
        - **Every frame must belong to the Mission, and each Drone appears once.**
        - The list may be empty.
        - **A WebSocket message has no headers, so the trace parent travels in the frame:** the browser continues the
          trace of the tick that built it. It is optional, and neither id may be all zeros.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    T_US_MIN: ClassVar[int] = 0
    TRACE_PARENT_PATTERN: ClassVar[str] = "^00-[0-9a-f]{32}-[0-9a-f]{16}-[0-9a-f]{2}$"
    TRACE_ID_ZEROS: ClassVar[str] = "0" * 32
    SPAN_ID_ZEROS: ClassVar[str] = "0" * 16

    mission_id: UUID = Field(description="The Mission of the frames.")
    t_us: int = Field(description="The moment of the tick, in microseconds since the epoch.")
    frames: List[TelemetryFrame] = Field(description="One frame per Drone.")
    trace_parent: Optional[str] = Field(
        default=None, description="The W3C trace parent of the tick that built the frame."
    )

    ############################
    # Publicly Exposed Methods #
    ############################

    @field_validator("mission_id", mode="before")
    def validate_mission_id(cls, value: JsonValue) -> UUID:
        """Validate ``mission_id``.

        Args:
            value (JsonValue): A version 7 UUID or its string form.

        Returns:
            UUID: The UUID.

        Raises:
            SESquadFrameInvalidMissionId: When the value is not a version 7 UUID.
        """
        return cls.parse_uuid7("mission_id", value, SESquadFrameInvalidMissionId)

    @field_validator("t_us", mode="before")
    def validate_t_us(cls, value: JsonValue) -> int:
        """Validate ``t_us``.

        Args:
            value (JsonValue): The raw value.

        Returns:
            int: The integer, within its bounds.

        Raises:
            SESquadFrameInvalidTUs: When the value is not an integer within its bounds.
        """
        return cls.parse_int("t_us", value, SESquadFrameInvalidTUs, cls.T_US_MIN, None)

    @field_validator("frames", mode="before")
    def validate_frames(cls, value: JsonValue) -> List[JsonValue]:
        """Validate ``frames``.

        Args:
            value (JsonValue): The frames, as a list.

        Returns:
            List[JsonValue]: The frames, which Pydantic then builds as ``TelemetryFrame``.

        Raises:
            SESquadFrameInvalidFrames: When the value is not a list.
        """
        if not isinstance(value, (list, tuple)):
            raise SESquadFrameInvalidFrames(f"Invalid frames: {value!r}. Must be a list of frames.")
        return list(value)

    @field_validator("trace_parent", mode="before")
    def validate_trace_parent(cls, value: JsonValue) -> Optional[str]:
        """Validate ``trace_parent``.

        Args:
            value (JsonValue): A W3C trace parent, or None.

        Returns:
            Optional[str]: The trace parent, or None.

        Raises:
            SESquadFrameInvalidTraceParent: When the value is not a valid W3C trace parent.
        """
        if value is None:
            return None
        if not isinstance(value, str) or not re.fullmatch(cls.TRACE_PARENT_PATTERN, value):
            raise SESquadFrameInvalidTraceParent(
                f"Invalid trace_parent: {value!r}. "
                "Must be a lower case W3C trace parent such as 00-<32 hex>-<16 hex>-<2 hex>."
            )
        _, trace_id, span_id, _ = value.split("-")
        if trace_id == cls.TRACE_ID_ZEROS or span_id == cls.SPAN_ID_ZEROS:
            raise SESquadFrameInvalidTraceParent(
                f"Invalid trace_parent: {value!r}. Must not hold an all-zero trace id or span id."
            )
        return value

    @model_validator(mode="after")
    def validate_frames_of_the_mission(self) -> SquadFrame:
        """Check that every frame belongs to the Mission and that no Drone appears twice.

        Returns:
            SquadFrame: The same squad frame.

        Raises:
            SESquadFrameMissionMismatch: When a frame belongs to another Mission.
            SESquadFrameDuplicateDrone: When two frames come from the same Drone.
        """
        seen: Set[UUID] = set()
        for frame in self.frames:
            if frame.mission_id != self.mission_id:
                raise SESquadFrameMissionMismatch(
                    f"Invalid frames: frame of Mission {frame.mission_id}. Must belong to Mission {self.mission_id}."
                )
            if frame.drone_id in seen:
                raise SESquadFrameDuplicateDrone(
                    f"Invalid frames: Drone {frame.drone_id} appears twice. Must hold one frame per Drone."
                )
            seen.add(frame.drone_id)
        return self
