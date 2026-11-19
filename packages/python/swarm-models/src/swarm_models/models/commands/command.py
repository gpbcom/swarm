"""The Command model."""

from __future__ import annotations

# Standard library imports
from typing import ClassVar, FrozenSet, Optional
from uuid import UUID

# Third-party imports
from pydantic import ConfigDict, Field, JsonValue, field_validator, model_validator

# First-party imports
from swarm_models.models.base.swarm_model import SwarmModel
from swarm_models.models.commands.enums import CommandKind, CommandLane
from swarm_models.models.commands.exceptions import (
    SECommandInvalidDroneId,
    SECommandInvalidId,
    SECommandInvalidIssuedBy,
    SECommandInvalidKind,
    SECommandInvalidLane,
    SECommandInvalidMissionId,
    SECommandWrongLane,
)


class Command(SwarmModel):
    """An order given to one Drone or to the whole Squad, in a Mission.

    Attributes:
        model_config (ConfigDict): Forbids unknown keys and freezes the command.
        SAFETY_KINDS (ClassVar[FrozenSet[CommandKind]]): The kinds that travel in the safety lane.
        id (UUID): The version 7 identifier of the command.
        mission_id (UUID): The Mission the command belongs to.
        drone_id (Optional[UUID]): The Drone targeted, or ``None`` for the whole Squad.
        kind (CommandKind): What the command asks.
        issued_by (UUID): Who issued the command.
        lane (CommandLane): The lane the command travels in.

    Notes:
        - The safety lane always jumps the queue, and the normal lane is for the rest.
        - **A safety kind on the normal lane is refused**, so that a safety order never waits.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    SAFETY_KINDS: ClassVar[FrozenSet[CommandKind]] = frozenset(
        {CommandKind.HOLD, CommandKind.ABORT, CommandKind.RETURN_HOME, CommandKind.MANUAL_CONTROL}
    )

    id: UUID = Field(description="The version 7 identifier of the command.")
    mission_id: UUID = Field(description="The Mission the command belongs to.")
    drone_id: Optional[UUID] = Field(default=None, description="The Drone targeted, or none for the whole Squad.")
    kind: CommandKind = Field(description="What the command asks.")
    issued_by: UUID = Field(description="Who issued the command.")
    lane: CommandLane = Field(description="The lane the command travels in.")

    @field_validator("id", mode="before")
    def validate_id(cls, value: JsonValue) -> UUID:
        """Validate ``id``.

        Args:
            value (JsonValue): The raw value.

        Returns:
            UUID: The version 7 UUID.
        """
        return cls.parse_uuid7("id", value, SECommandInvalidId)

    @field_validator("mission_id", mode="before")
    def validate_mission_id(cls, value: JsonValue) -> UUID:
        """Validate ``mission_id``.

        Args:
            value (JsonValue): The raw value.

        Returns:
            UUID: The version 7 UUID.
        """
        return cls.parse_uuid7("mission_id", value, SECommandInvalidMissionId)

    @field_validator("drone_id", mode="before")
    def validate_drone_id(cls, value: JsonValue) -> Optional[UUID]:
        """Validate ``drone_id``, where ``None`` targets the whole Squad.

        Args:
            value (JsonValue): The raw value.

        Returns:
            Optional[UUID]: The version 7 UUID, or ``None``.
        """
        if value is None:
            return cls.model_fields["drone_id"].get_default(call_default_factory=True)
        return cls.parse_uuid7("drone_id", value, SECommandInvalidDroneId)

    @field_validator("kind", mode="before")
    def validate_kind(cls, value: JsonValue) -> CommandKind:
        """Validate ``kind``.

        Args:
            value (JsonValue): The raw value.

        Returns:
            CommandKind: The kind.

        Raises:
            SECommandInvalidKind: When the value is not a known kind.
        """
        if isinstance(value, str) and value in {member.value for member in CommandKind}:
            return CommandKind(value)
        raise SECommandInvalidKind(
            f"Invalid kind: {value!r}. Must be one of {[member.value for member in CommandKind]}."
        )

    @field_validator("issued_by", mode="before")
    def validate_issued_by(cls, value: JsonValue) -> UUID:
        """Validate ``issued_by``.

        Args:
            value (JsonValue): The raw value.

        Returns:
            UUID: The version 7 UUID.
        """
        return cls.parse_uuid7("issued_by", value, SECommandInvalidIssuedBy)

    @field_validator("lane", mode="before")
    def validate_lane(cls, value: JsonValue) -> CommandLane:
        """Validate ``lane``.

        Args:
            value (JsonValue): The raw value.

        Returns:
            CommandLane: The lane.

        Raises:
            SECommandInvalidLane: When the value is not a known lane.
        """
        if isinstance(value, str) and value in {member.value for member in CommandLane}:
            return CommandLane(value)
        raise SECommandInvalidLane(
            f"Invalid lane: {value!r}. Must be one of {[member.value for member in CommandLane]}."
        )

    @model_validator(mode="after")
    def validate_lane_of_kind(self) -> Command:
        """Check that a safety kind is not on the normal lane.

        Returns:
            Command: The command itself.

        Raises:
            SECommandWrongLane: When a safety kind is on the normal lane.
        """
        if self.kind in self.SAFETY_KINDS and self.lane is not CommandLane.SAFETY:
            raise SECommandWrongLane(
                f"Invalid lane: {self.lane.value!r}. "
                f"Must be {CommandLane.SAFETY.value!r} for the kind {self.kind.value!r}."
            )
        return self
