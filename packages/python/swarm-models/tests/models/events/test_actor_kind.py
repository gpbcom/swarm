from __future__ import annotations

from enum import StrEnum

import pytest

from swarm_models.models.events.enums import ActorKind


class TestActorKind:
    def test_the_members_and_their_values(self) -> None:
        assert {member.name: member.value for member in ActorKind} == {
            "PERSON": "person",
            "SWARM_AGENT": "swarm_agent",
            "OUTSIDE_AGENT": "outside_agent",
        }

    def test_it_is_a_string_enum(self) -> None:
        assert issubclass(ActorKind, StrEnum)
        assert ActorKind.PERSON == "person"

    @pytest.mark.parametrize(
        ("value", "member"),
        [
            ("person", ActorKind.PERSON),
            ("swarm_agent", ActorKind.SWARM_AGENT),
            ("outside_agent", ActorKind.OUTSIDE_AGENT),
        ],
    )
    def test_a_member_is_built_from_its_string(self, value: str, member: ActorKind) -> None:
        assert ActorKind(value) is member

    @pytest.mark.parametrize("value", ["robot", "", "Person", "swarm agent"])
    def test_an_unknown_string_raises_a_value_error(self, value: str) -> None:
        with pytest.raises(ValueError):
            ActorKind(value)
