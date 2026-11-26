from __future__ import annotations

# Third-party imports
import pytest

# First-party imports
from swarm_models.commands.enums import CommandLane


class TestCommandLane:
    def test_the_members_and_their_values(self) -> None:
        assert [(member.name, member.value) for member in CommandLane] == [("SAFETY", "safety"), ("NORMAL", "normal")]

    @pytest.mark.parametrize(("text", "expected"), [("safety", CommandLane.SAFETY), ("normal", CommandLane.NORMAL)])
    def test_a_member_is_built_from_its_string(self, text: str, expected: CommandLane) -> None:
        assert CommandLane(text) is expected

    def test_an_unknown_string_is_refused(self) -> None:
        with pytest.raises(ValueError):
            CommandLane("fast")
