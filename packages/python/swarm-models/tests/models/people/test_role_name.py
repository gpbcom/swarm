from __future__ import annotations

from enum import StrEnum
from typing import ClassVar, Dict

import pytest

from swarm_models.models.people.enums import RoleName


class TestRoleName:
    VALUES: ClassVar[Dict[str, str]] = {
        "PILOT": "pilot",
        "MISSION_PLANNER": "mission_planner",
        "FLEET_MAINTAINER": "fleet_maintainer",
        "INSTRUCTOR": "instructor",
        "CLIENT": "client",
        "SITE_AGENT": "site_agent",
        "SWARM_ADMINISTRATOR": "swarm_administrator",
    }

    def test_it_is_a_string_enum(self) -> None:
        assert issubclass(RoleName, StrEnum)

    def test_the_members_and_their_values(self) -> None:
        assert {member.name: member.value for member in RoleName} == self.VALUES

    @pytest.mark.parametrize("value", list(VALUES.values()))
    def test_a_member_is_built_from_its_string(self, value: str) -> None:
        assert RoleName(value).value == value

    def test_an_unknown_string_raises_a_value_error(self) -> None:
        with pytest.raises(ValueError):
            RoleName("pilot-in-chief")
