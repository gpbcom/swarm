from __future__ import annotations

# Third-party imports
import pytest

# First-party imports
from swarm_models.models.commands.enums import CommandKind


class TestCommandKind:
    def test_the_members_and_their_values(self) -> None:
        assert [(member.name, member.value) for member in CommandKind] == [
            ("HOLD", "hold"),
            ("ABORT", "abort"),
            ("RETURN_HOME", "return_home"),
            ("MANUAL_CONTROL", "manual_control"),
        ]

    @pytest.mark.parametrize(
        ("text", "expected"),
        [
            ("hold", CommandKind.HOLD),
            ("abort", CommandKind.ABORT),
            ("return_home", CommandKind.RETURN_HOME),
            ("manual_control", CommandKind.MANUAL_CONTROL),
        ],
    )
    def test_a_member_is_built_from_its_string(self, text: str, expected: CommandKind) -> None:
        assert CommandKind(text) is expected

    def test_an_unknown_string_is_refused(self) -> None:
        with pytest.raises(ValueError):
            CommandKind("jump")
