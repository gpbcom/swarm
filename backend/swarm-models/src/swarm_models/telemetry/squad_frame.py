from __future__ import annotations

# Standard library imports
from typing import ClassVar, List, Set
from uuid import UUID

# Third-party imports
from pydantic import ConfigDict, Field, JsonValue, field_validator, model_validator

# First-party imports
from swarm_models.base.swarm_model import SwarmModel
from swarm_models.telemetry.exceptions import (
    SESquadFrameDuplicateDrone,
    SESquadFrameInvalidFrames,
    SESquadFrameInvalidMissionId,
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
        T_US_MIN (ClassVar[int]): The smallest accepted ``t_us``.

    Notes:
        - **Every frame must belong to the Mission, and each Drone appears once.**
        - The list may be empty.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    T_US_MIN: ClassVar[int] = 0

    mission_id: UUID = Field(description="The Mission of the frames.")
    t_us: int = Field(description="The moment of the tick, in microseconds since the epoch.")
    frames: List[TelemetryFrame] = Field(description="One frame per Drone.")

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
