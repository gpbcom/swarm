from __future__ import annotations

# Standard library imports
from re import fullmatch
from typing import ClassVar, Literal, Union
from uuid import UUID

# Third-party imports
from pydantic import ConfigDict, Field, JsonValue, field_validator

# First-party imports
from swarm_models.base.swarm_model import SwarmModel
from swarm_models.events.event import Event
from swarm_nats.models.subjects.exceptions import (
    SEOperatorSubjectsInvalidEvent,
    SEOperatorSubjectsInvalidMissionId,
    SEOperatorSubjectsInvalidOperatorId,
    SEOperatorSubjectsOperatorMismatch,
)


class OperatorSubjects(SwarmModel):
    """The NATS subjects of one Operator.

    Attributes:
        model_config (ConfigDict): Forbids unknown keys and freezes the subjects.
        OPERATOR_ID_FIELD (ClassVar[str]): The name of the ``operator_id`` field.
        MISSION_ID_FIELD (ClassVar[str]): The name of the ``mission_id`` argument.
        BEFORE (ClassVar[Literal["before"]]): The mode of the validators.
        PREFIX (ClassVar[str]): The first token of every subject.
        MISSION (ClassVar[str]): The token of the subjects of a Mission.
        FLEET (ClassVar[str]): The token of the subjects of the fleet.
        ALL (ClassVar[str]): The wildcard that matches every token below.
        SEPARATOR (ClassVar[str]): The separator of the tokens.
        EVENT_PATTERN (ClassVar[str]): The shape of an event name, lower case words separated by dots.
        operator_id (UUID): The Operator the subjects belong to, a version 7 UUID.

    Notes:
        - Subjects follow ``op.<operator_id>.mission.<mission_id>.<event>`` and ``op.<operator_id>.fleet.<event>``, so
          permissions and streams split by Operator.
        - **An event of another Operator is refused**, so that a subject never crosses the isolation of Operators.
        - The ``<event>`` token is the type of the event, unchanged.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    OPERATOR_ID_FIELD: ClassVar[str] = "operator_id"
    MISSION_ID_FIELD: ClassVar[str] = "mission_id"
    BEFORE: ClassVar[Literal["before"]] = "before"
    PREFIX: ClassVar[str] = "op"
    MISSION: ClassVar[str] = "mission"
    FLEET: ClassVar[str] = "fleet"
    ALL: ClassVar[str] = ">"
    SEPARATOR: ClassVar[str] = "."
    EVENT_PATTERN: ClassVar[str] = r"[a-z0-9_]+(\.[a-z0-9_]+)*"

    operator_id: UUID = Field(description="The Operator the subjects belong to, a version 7 UUID.")

    @field_validator(OPERATOR_ID_FIELD, mode=BEFORE)
    def validate_operator_id(cls, value: JsonValue) -> JsonValue:
        """Validate ``operator_id``.

        Args:
            value (JsonValue): The raw value.

        Returns:
            JsonValue: The identifier.

        Raises:
            SEOperatorSubjectsInvalidOperatorId: When the value is not a version 7 UUID.
        """
        return str(cls.parse_uuid7(cls.OPERATOR_ID_FIELD, value, SEOperatorSubjectsInvalidOperatorId))

    ############################
    # Internal Helpers Methods #
    ############################

    def _event_token(self, event: JsonValue) -> str:
        """Check an event name.

        Args:
            event (JsonValue): The raw event name.

        Returns:
            str: The event name.

        Raises:
            SEOperatorSubjectsInvalidEvent: When the value does not match ``EVENT_PATTERN``.
        """
        if not isinstance(event, str) or fullmatch(self.EVENT_PATTERN, event) is None:
            raise SEOperatorSubjectsInvalidEvent(f"Invalid event: {event!r}. Must match {self.EVENT_PATTERN!r}.")
        return event

    ############################
    # Publicly Exposed Methods #
    ############################

    def all(self) -> str:
        """Give the subject that covers everything of the Operator.

        Returns:
            str: The subject, ``op.<operator_id>.>``.
        """
        return self.SEPARATOR.join([self.PREFIX, str(self.operator_id), self.ALL])

    def mission(self, mission_id: Union[UUID, JsonValue], event: JsonValue) -> str:
        """Give the subject of an event of a Mission.

        Args:
            mission_id (Union[UUID, JsonValue]): The Mission, a version 7 UUID or its string form.
            event (JsonValue): The name of the event.

        Returns:
            str: The subject, ``op.<operator_id>.mission.<mission_id>.<event>``.

        Raises:
            SEOperatorSubjectsInvalidMissionId: When the Mission is not a version 7 UUID.
            SEOperatorSubjectsInvalidEvent: When the event name is refused.
        """
        raw: JsonValue
        if isinstance(mission_id, UUID):
            raw = str(mission_id)
        else:
            raw = mission_id
        mission = self.parse_uuid7(self.MISSION_ID_FIELD, raw, SEOperatorSubjectsInvalidMissionId)
        token = self._event_token(event)
        return self.SEPARATOR.join([self.PREFIX, str(self.operator_id), self.MISSION, str(mission), token])

    def fleet(self, event: JsonValue) -> str:
        """Give the subject of an event of the fleet.

        Args:
            event (JsonValue): The name of the event.

        Returns:
            str: The subject, ``op.<operator_id>.fleet.<event>``.

        Raises:
            SEOperatorSubjectsInvalidEvent: When the event name is refused.
        """
        token = self._event_token(event)
        return self.SEPARATOR.join([self.PREFIX, str(self.operator_id), self.FLEET, token])

    def for_event(self, event: Event) -> str:
        """Give the subject an event is published on.

        Args:
            event (Event): The event.

        Returns:
            str: The subject of its Mission, or of the fleet when it has no Mission.

        Raises:
            SEOperatorSubjectsOperatorMismatch: When the event belongs to another Operator.
        """
        if event.operator_id != self.operator_id:
            raise SEOperatorSubjectsOperatorMismatch(
                f"Invalid operator_id: {str(event.operator_id)!r}. "
                f"Must be {str(self.operator_id)!r}, the Operator of these subjects."
            )
        if event.mission_id is None:
            return self.fleet(event.type)
        return self.mission(event.mission_id, event.type)
