from __future__ import annotations

# Standard library imports
from enum import StrEnum
from typing import ClassVar, Dict, Type

# Third-party imports
import pytest

# First-party imports
from swarm_i18n.models.enums import MessageProblem


class TestSwarmI18nEnums:
    EXPECTED: ClassVar[Dict[Type[StrEnum], Dict[str, str]]] = {
        MessageProblem: {"MISSING": "missing", "EMPTY": "empty", "FUZZY": "fuzzy"},
    }

    @pytest.mark.parametrize("enum", [MessageProblem])
    def test_the_members_and_values_are_exactly_the_contract(self, enum: Type[StrEnum]) -> None:
        assert {member.name: member.value for member in enum} == self.EXPECTED[enum]

    @pytest.mark.parametrize("enum", [MessageProblem])
    def test_each_enum_is_a_str_enum(self, enum: Type[StrEnum]) -> None:
        assert issubclass(enum, StrEnum)

    @pytest.mark.parametrize("enum", [MessageProblem])
    def test_the_values_are_unique(self, enum: Type[StrEnum]) -> None:
        values = [member.value for member in enum]
        assert len(values) == len(set(values))

    @pytest.mark.parametrize("enum", [MessageProblem])
    def test_no_value_contains_a_hyphen(self, enum: Type[StrEnum]) -> None:
        assert all("-" not in member.value for member in enum)
