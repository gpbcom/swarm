from __future__ import annotations

# Standard library imports
from typing import ClassVar, Literal, Optional, Self
from uuid import UUID

# Third-party imports
from pydantic import ConfigDict, Field, JsonValue, field_validator, model_validator

# First-party imports
from swarm_models.base.swarm_model import SwarmModel
from swarm_models.enums import CommandVerdict
from swarm_models.simulation.commands.exceptions import (
    SECommandReplyInvalidCommandId,
    SECommandReplyInvalidReason,
    SECommandReplyInvalidVerdict,
    SECommandReplyRefusedWithoutReason,
)


class CommandReply(SwarmModel):
    """The Simulator's answer to one command.

    Attributes:
        model_config (ConfigDict): Forbids unknown keys and freezes the model.
        COMMAND_ID_FIELD (str): The name of the ``command_id`` field.
        VERDICT_FIELD (str): The name of the ``verdict`` field.
        REASON_FIELD (str): The name of the ``reason`` field.
        BEFORE (str): The validator mode that runs before Pydantic's own validation.
        command_id (UUID): The identifier of the command, a version 7 UUID.
        verdict (CommandVerdict): Whether the command was accepted or refused.
        reason (Optional[str]): Why, mandatory when the command is refused.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    COMMAND_ID_FIELD: ClassVar[str] = "command_id"
    VERDICT_FIELD: ClassVar[str] = "verdict"
    REASON_FIELD: ClassVar[str] = "reason"
    BEFORE: ClassVar[Literal["before"]] = "before"

    command_id: UUID = Field(description="The identifier of the command, a version 7 UUID.")
    verdict: CommandVerdict = Field(description="Whether the command was accepted or refused.")
    reason: Optional[str] = Field(default=None, description="Why, mandatory when the command is refused.")

    @field_validator(COMMAND_ID_FIELD, mode=BEFORE)
    def validate_command_id(cls, value: JsonValue) -> UUID:
        """Validate ``command_id``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            UUID: The version 7 UUID.

        Raises:
            SECommandReplyInvalidCommandId: If the value is not a version 7 UUID.
        """
        return cls.parse_uuid7(cls.COMMAND_ID_FIELD, value, SECommandReplyInvalidCommandId)

    @field_validator(VERDICT_FIELD, mode=BEFORE)
    def validate_verdict(cls, value: JsonValue) -> CommandVerdict:
        """Validate ``verdict``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            CommandVerdict: The verdict.

        Raises:
            SECommandReplyInvalidVerdict: If the value is not a verdict.
        """
        if not isinstance(value, str) or value not in CommandVerdict:
            raise SECommandReplyInvalidVerdict(
                f"Invalid verdict: {value!r}. Must be one of {[verdict.value for verdict in CommandVerdict]}."
            )
        return CommandVerdict(value)

    @field_validator(REASON_FIELD, mode=BEFORE)
    def validate_reason(cls, value: JsonValue) -> Optional[str]:
        """Validate ``reason``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            Optional[str]: The stripped reason, or ``None``.

        Raises:
            SECommandReplyInvalidReason: If the value is not a non-empty string.
        """
        if value is None:
            return None
        return cls.parse_text(cls.REASON_FIELD, value, SECommandReplyInvalidReason)

    @model_validator(mode="after")
    def validate_refusal_has_reason(self) -> Self:
        """Check that a refused reply says why.

        Returns:
            Self: The reply.

        Raises:
            SECommandReplyRefusedWithoutReason: If the reply is refused and has no reason.
        """
        if self.verdict == CommandVerdict.REFUSED and self.reason is None:
            raise SECommandReplyRefusedWithoutReason("Invalid reason: None. Must be given when the verdict is refused.")
        return self
