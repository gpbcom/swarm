from __future__ import annotations

# Standard library imports
from typing import Optional
from uuid import UUID

# Third-party imports
from pydantic import ConfigDict, Field, JsonValue, field_validator, model_validator

# First-party imports
from swarm_models.models.base.swarm_model import SwarmModel
from swarm_models.models.events.enums import ActorKind
from swarm_models.models.events.exceptions import (
    SEActorInconsistentKind,
    SEActorInvalidAgentName,
    SEActorInvalidKind,
    SEActorInvalidPersonId,
)


class Actor(SwarmModel):
    """The author of an event.

    Attributes:
        model_config (ConfigDict): Forbids unknown keys and freezes the actor.
        kind (ActorKind): Whether the author is a person, a Swarm agent or an outside agent.
        person_id (Optional[UUID]): The person, who is the author or the person the agent acts for.
        agent_name (Optional[str]): The name of the agent, for an agent.

    Notes:
        - A person has a ``person_id`` and no ``agent_name``.
        - A Swarm agent has an ``agent_name`` and may act for a person.
        - **An outside agent always has both**, because it never acts without the person it acts for.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    kind: ActorKind = Field(description="Whether the author is a person, a Swarm agent or an outside agent.")
    person_id: Optional[UUID] = Field(
        default=None, description="The person who is the author, or the person the agent acts for."
    )
    agent_name: Optional[str] = Field(default=None, description="The name of the agent, for an agent.")

    @field_validator("kind", mode="before")
    def validate_kind(cls, value: JsonValue) -> JsonValue:
        """Validate ``kind``.

        Args:
            value (JsonValue): The raw value.

        Returns:
            JsonValue: The kind.

        Raises:
            SEActorInvalidKind: When the value is not a kind.
        """
        if isinstance(value, ActorKind):
            return value
        if isinstance(value, str):
            try:
                return ActorKind(value)
            except ValueError as error:
                raise SEActorInvalidKind(
                    f"Invalid kind: {value!r}. Must be one of {[member.value for member in ActorKind]}."
                ) from error
        raise SEActorInvalidKind(f"Invalid kind: {value!r}. Must be one of {[member.value for member in ActorKind]}.")

    @field_validator("person_id", mode="before")
    def validate_person_id(cls, value: JsonValue) -> JsonValue:
        """Validate ``person_id``.

        Args:
            value (JsonValue): The raw value.

        Returns:
            JsonValue: The identifier, or ``None``.

        Raises:
            SEActorInvalidPersonId: When the value is not a version 7 UUID.
        """
        if value is None:
            return cls.model_fields["person_id"].get_default(call_default_factory=True)
        return str(cls.parse_uuid7("person_id", value, SEActorInvalidPersonId))

    @field_validator("agent_name", mode="before")
    def validate_agent_name(cls, value: JsonValue) -> JsonValue:
        """Validate ``agent_name``.

        Args:
            value (JsonValue): The raw value.

        Returns:
            JsonValue: The stripped name, or ``None``.

        Raises:
            SEActorInvalidAgentName: When the value is not a non-empty string.
        """
        if value is None:
            return cls.model_fields["agent_name"].get_default(call_default_factory=True)
        return cls.parse_text("agent_name", value, SEActorInvalidAgentName)

    @model_validator(mode="after")
    def validate_kind_rule(self) -> Actor:
        """Check that the identifiers fit the kind.

        Returns:
            Actor: The same actor.

        Raises:
            SEActorInconsistentKind: When the identifiers do not fit the kind.
        """
        has_person = self.person_id is not None
        has_agent = self.agent_name is not None
        match self.kind:
            case ActorKind.PERSON:
                consistent = has_person and not has_agent
            case ActorKind.SWARM_AGENT:
                consistent = has_agent
            case ActorKind.OUTSIDE_AGENT:
                consistent = has_person and has_agent
        if not consistent:
            raise SEActorInconsistentKind(
                f"Inconsistent kind: {self.kind.value!r}. "
                "A person needs a person_id and no agent_name. "
                "A Swarm agent needs an agent_name. "
                "An outside agent needs both."
            )
        return self
