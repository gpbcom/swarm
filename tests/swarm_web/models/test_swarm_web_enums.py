from __future__ import annotations

# Standard library imports
from enum import StrEnum

# Third-party imports
import pytest

# First-party imports
from swarm_web.models.enums import SignalAttribute


class TestSwarmWebEnums:
    def test_signal_attribute_is_a_string_enum(self) -> None:
        assert issubclass(SignalAttribute, StrEnum)

    @pytest.mark.parametrize("name", ["OPERATOR_ID", "MISSION_ID", "CELL", "DRONE_ID"])
    def test_the_signal_attributes_exist(self, name: str) -> None:
        assert name in SignalAttribute.__members__

    def test_each_signal_attribute_is_the_lower_case_of_its_name(self) -> None:
        for member in SignalAttribute:
            assert member.value == member.name.lower()

    def test_the_signal_attributes_are_unique(self) -> None:
        values = [member.value for member in SignalAttribute]
        assert len(values) == len(set(values))

    def test_no_value_contains_a_hyphen(self) -> None:
        assert all("-" not in member.value for member in SignalAttribute)
