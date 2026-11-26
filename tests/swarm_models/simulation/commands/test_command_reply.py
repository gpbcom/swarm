from __future__ import annotations

# Standard library imports
from typing import ClassVar, Dict
from uuid import UUID

# Third-party imports
import pytest
from pydantic import JsonValue, ValidationError

# First-party imports
from swarm_models.enums import CommandVerdict
from swarm_models.simulation.commands.command_reply import CommandReply
from swarm_models.simulation.commands.exceptions import (
    SECommandReplyInvalidCommandId,
    SECommandReplyInvalidReason,
    SECommandReplyInvalidVerdict,
    SECommandReplyRefusedWithoutReason,
)


class TestCommandReply:
    COMMAND_ID: ClassVar[str] = "01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e5f"
    VERSION_4_ID: ClassVar[str] = "3f2b8c1e-5d4a-4b6c-8e7f-9a0b1c2d3e4f"
    ACCEPTED: ClassVar[Dict[str, JsonValue]] = {
        "command_id": COMMAND_ID,
        "verdict": CommandVerdict.ACCEPTED.value,
    }
    REFUSED: ClassVar[Dict[str, JsonValue]] = {
        "command_id": COMMAND_ID,
        "verdict": CommandVerdict.REFUSED.value,
        "reason": "Unknown Drone.",
    }
    UNKNOWN_KEY: ClassVar[Dict[str, JsonValue]] = {**ACCEPTED, "colour": "red"}

    def test_defaults(self) -> None:
        reply = CommandReply.model_validate(self.ACCEPTED)
        assert reply.verdict == CommandVerdict.ACCEPTED
        assert reply.reason is None

    def test_full_valid_construction(self) -> None:
        reply = CommandReply(
            command_id=UUID(self.COMMAND_ID),
            verdict=CommandVerdict.REFUSED,
            reason="Unknown Drone.",
        )
        assert reply.command_id == UUID(self.COMMAND_ID)
        assert reply.verdict == CommandVerdict.REFUSED
        assert reply.reason == "Unknown Drone."

    def test_none_becomes_the_default(self) -> None:
        reply = CommandReply.model_validate({**self.ACCEPTED, "reason": None})
        default = CommandReply.model_fields["reason"].get_default(call_default_factory=True)
        assert reply.reason == default

    @pytest.mark.parametrize(
        ("name", "value", "error"),
        [
            ("command_id", "not-a-uuid", SECommandReplyInvalidCommandId),
            ("command_id", VERSION_4_ID, SECommandReplyInvalidCommandId),
            ("command_id", 3, SECommandReplyInvalidCommandId),
            ("verdict", "maybe", SECommandReplyInvalidVerdict),
            ("verdict", 3, SECommandReplyInvalidVerdict),
            ("reason", "", SECommandReplyInvalidReason),
            ("reason", "   ", SECommandReplyInvalidReason),
            ("reason", 3, SECommandReplyInvalidReason),
        ],
    )
    def test_rejects_bad_values(self, name: str, value: JsonValue, error: type[Exception]) -> None:
        with pytest.raises(error):
            CommandReply.model_validate({**self.ACCEPTED, name: value})

    def test_rejects_unknown_keys(self) -> None:
        with pytest.raises(ValidationError):
            CommandReply.model_validate(self.UNKNOWN_KEY)

    def test_round_trip(self) -> None:
        reply = CommandReply.model_validate(self.REFUSED)
        assert CommandReply.model_validate(reply.model_dump()) == reply
        assert CommandReply.model_validate_json(reply.model_dump_json()) == reply

    def test_a_refused_reply_without_a_reason_is_refused(self) -> None:
        with pytest.raises(SECommandReplyRefusedWithoutReason):
            CommandReply.model_validate({**self.ACCEPTED, "verdict": CommandVerdict.REFUSED.value})

    def test_a_refused_reply_with_a_reason_is_accepted(self) -> None:
        reply = CommandReply.model_validate(self.REFUSED)
        assert reply.verdict == CommandVerdict.REFUSED

    def test_an_accepted_reply_may_carry_a_reason(self) -> None:
        reply = CommandReply.model_validate({**self.ACCEPTED, "reason": "Done."})
        assert reply.reason == "Done."

    def test_the_reason_is_stripped(self) -> None:
        reply = CommandReply.model_validate({**self.REFUSED, "reason": "  Unknown Drone. "})
        assert reply.reason == "Unknown Drone."

    def test_a_reply_is_frozen(self) -> None:
        reply = CommandReply.model_validate(self.ACCEPTED)
        with pytest.raises(ValidationError):
            reply.reason = "later"
