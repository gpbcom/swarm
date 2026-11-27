from __future__ import annotations

# Standard library imports
from enum import StrEnum
from typing import ClassVar, Dict, List, Type

# Third-party imports
import pytest

# First-party imports
from swarm_models.enums import Anchoring, Deployment, Jurisdiction, LlmProvider, OperatorField


class TestOperatorEnums:
    EXPECTED: ClassVar[Dict[Type[StrEnum], Dict[str, str]]] = {
        Deployment: {"CLOUD": "cloud", "ON_PREMISES": "on_premises"},
        Jurisdiction: {"EU_EASA": "eu_easa", "US_FAA": "us_faa"},
        LlmProvider: {"CLAUDE": "claude", "OPEN_WEIGHT": "open_weight"},
        Anchoring: {
            "QUALIFIED_TIMESTAMPING": "qualified_timestamping",
            "PUBLIC_BLOCKCHAIN": "public_blockchain",
            "NONE": "none",
        },
        OperatorField: {
            "NAME": "name",
            "DEPLOYMENT": "deployment",
            "JURISDICTIONS": "jurisdictions",
            "FIRST_MISSION_PLANNER_EMAIL": "first_mission_planner_email",
        },
    }
    ENUMS: ClassVar[List[Type[StrEnum]]] = [Deployment, Jurisdiction, LlmProvider, Anchoring, OperatorField]

    @pytest.mark.parametrize("enum", ENUMS)
    def test_the_members_and_values_are_exactly_the_contract(self, enum: Type[StrEnum]) -> None:
        assert {member.name: member.value for member in enum} == self.EXPECTED[enum]

    @pytest.mark.parametrize("enum", ENUMS)
    def test_each_enum_is_a_str_enum(self, enum: Type[StrEnum]) -> None:
        assert issubclass(enum, StrEnum)

    @pytest.mark.parametrize("enum", ENUMS)
    def test_the_values_are_unique(self, enum: Type[StrEnum]) -> None:
        values = [member.value for member in enum]
        assert len(values) == len(set(values))

    @pytest.mark.parametrize("enum", ENUMS)
    def test_the_values_are_lower_snake_case_without_hyphen(self, enum: Type[StrEnum]) -> None:
        assert all("-" not in member.value and member.value == member.value.lower() for member in enum)
