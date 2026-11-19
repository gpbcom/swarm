from __future__ import annotations

# Standard library imports
from datetime import datetime
from re import fullmatch
from typing import ClassVar, Dict, Mapping, Optional, Union
from uuid import UUID

# Third-party imports
from pydantic import ConfigDict, Field, JsonValue, field_validator

# First-party imports
from swarm_models.models.base.swarm_model import SwarmModel
from swarm_models.models.events.actor import Actor
from swarm_models.models.events.exceptions import (
    SEEventInvalidActor,
    SEEventInvalidId,
    SEEventInvalidMissionId,
    SEEventInvalidOccurredAt,
    SEEventInvalidOperatorId,
    SEEventInvalidPayload,
    SEEventInvalidType,
    SEEventInvalidVersion,
)


class Event(SwarmModel):
    """The envelope of every change published by Swarm.

    Attributes:
        model_config (ConfigDict): Forbids unknown keys and freezes the event.
        TYPE_PATTERN (ClassVar[str]): The shape of a type, such as ``mission.planned``.
        VERSION_MIN (ClassVar[int]): The smallest version of an event.
        id (UUID): The identifier, a version 7 UUID.
        type (str): The type, lower case words separated by dots.
        version (int): The version of the type.
        operator_id (UUID): The Operator the event belongs to.
        mission_id (Optional[UUID]): The Mission the event is about, none for a fleet event.
        occurred_at (datetime): When it happened, in UTC with microseconds.
        actor (Actor): Who did it.
        payload (Dict[str, JsonValue]): The model that changed.

    Notes:
        - **The event is frozen**, because a published event is never edited.
        - An ``actor`` given as a mapping becomes an ``Actor``, and the errors of the actor are raised unchanged.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    TYPE_PATTERN: ClassVar[str] = r"[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+"
    VERSION_MIN: ClassVar[int] = 1

    id: UUID = Field(description="The identifier, a version 7 UUID.")
    type: str = Field(description="The type, lower case words separated by dots.")
    version: int = Field(default=1, description="The version of the type.")
    operator_id: UUID = Field(description="The Operator the event belongs to.")
    mission_id: Optional[UUID] = Field(
        default=None, description="The Mission the event is about, none for a fleet event."
    )
    occurred_at: datetime = Field(description="When it happened, in UTC with microseconds.")
    actor: Actor = Field(description="Who did it.")
    payload: Dict[str, JsonValue] = Field(description="The model that changed.")

    @field_validator("id", mode="before")
    def validate_id(cls, value: JsonValue) -> JsonValue:
        """Validate ``id``.

        Args:
            value (JsonValue): The raw value.

        Returns:
            JsonValue: The identifier.

        Raises:
            SEEventInvalidId: When the value is not a version 7 UUID.
        """
        return str(cls.parse_uuid7("id", value, SEEventInvalidId))

    @field_validator("type", mode="before")
    def validate_type(cls, value: JsonValue) -> JsonValue:
        """Validate ``type``.

        Args:
            value (JsonValue): The raw value.

        Returns:
            JsonValue: The stripped type.

        Raises:
            SEEventInvalidType: When the value does not match ``TYPE_PATTERN``.
        """
        text = cls.parse_text("type", value, SEEventInvalidType)
        if fullmatch(cls.TYPE_PATTERN, text) is None:
            raise SEEventInvalidType(f"Invalid type: {value!r}. Must match {cls.TYPE_PATTERN!r}.")
        return text

    @field_validator("version", mode="before")
    def validate_version(cls, value: JsonValue) -> JsonValue:
        """Validate ``version``.

        Args:
            value (JsonValue): The raw value.

        Returns:
            JsonValue: The version.

        Raises:
            SEEventInvalidVersion: When the value is not an integer of at least ``VERSION_MIN``.
        """
        if value is None:
            return cls.model_fields["version"].get_default(call_default_factory=True)
        return cls.parse_int("version", value, SEEventInvalidVersion, minimum=cls.VERSION_MIN)

    @field_validator("operator_id", mode="before")
    def validate_operator_id(cls, value: JsonValue) -> JsonValue:
        """Validate ``operator_id``.

        Args:
            value (JsonValue): The raw value.

        Returns:
            JsonValue: The identifier.

        Raises:
            SEEventInvalidOperatorId: When the value is not a version 7 UUID.
        """
        return str(cls.parse_uuid7("operator_id", value, SEEventInvalidOperatorId))

    @field_validator("mission_id", mode="before")
    def validate_mission_id(cls, value: JsonValue) -> JsonValue:
        """Validate ``mission_id``.

        Args:
            value (JsonValue): The raw value.

        Returns:
            JsonValue: The identifier, or ``None``.

        Raises:
            SEEventInvalidMissionId: When the value is not a version 7 UUID.
        """
        if value is None:
            return cls.model_fields["mission_id"].get_default(call_default_factory=True)
        return str(cls.parse_uuid7("mission_id", value, SEEventInvalidMissionId))

    @field_validator("occurred_at", mode="before")
    def validate_occurred_at(cls, value: JsonValue) -> JsonValue:
        """Validate ``occurred_at``.

        Args:
            value (JsonValue): The raw value.

        Returns:
            JsonValue: The moment, in UTC.

        Raises:
            SEEventInvalidOccurredAt: When the value is not a moment with a time zone.
        """
        return cls.parse_utc("occurred_at", value, SEEventInvalidOccurredAt).isoformat()

    @field_validator("actor", mode="before")
    def validate_actor(cls, value: JsonValue) -> Union[Actor, JsonValue]:
        """Validate ``actor``.

        Args:
            value (JsonValue): An ``Actor`` or a mapping.

        Returns:
            Union[Actor, JsonValue]: The actor.

        Raises:
            SEEventInvalidActor: When the value is neither an actor nor a mapping.
        """
        if isinstance(value, Actor):
            return value
        if isinstance(value, Mapping):
            return Actor.model_validate(dict(value))
        raise SEEventInvalidActor(f"Invalid actor: {value!r}. Must be an Actor or a mapping.")

    @field_validator("payload", mode="before")
    def validate_payload(cls, value: JsonValue) -> JsonValue:
        """Validate ``payload``.

        Args:
            value (JsonValue): The raw value.

        Returns:
            JsonValue: The payload.

        Raises:
            SEEventInvalidPayload: When the value is not a mapping with string keys.
        """
        if not isinstance(value, Mapping) or not all(isinstance(key, str) for key in value):
            raise SEEventInvalidPayload(f"Invalid payload: {value!r}. Must be a mapping with string keys.")
        return dict(value)
