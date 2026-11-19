from __future__ import annotations

from typing import List

import pytest

from swarm_models.models.telemetry.enums import DroneState


class TestDroneState:
    def test_the_members_and_their_values(self) -> None:
        assert [(member.name, member.value) for member in DroneState] == [
            ("READY", "ready"),
            ("GROUNDED", "grounded"),
            ("AIRBORNE", "airborne"),
            ("RETURNING", "returning"),
            ("LANDED", "landed"),
            ("LOST", "lost"),
        ]

    @pytest.mark.parametrize("value", ["ready", "grounded", "airborne", "returning", "landed", "lost"])
    def test_a_state_is_built_from_its_string(self, value: str) -> None:
        assert DroneState(value).value == value
        assert DroneState(value) == value

    def test_the_members_are_unique(self) -> None:
        values: List[str] = [member.value for member in DroneState]
        assert len(values) == len(set(values)) == 6

    @pytest.mark.parametrize("value", ["flying", "READY", "", " ready"])
    def test_an_unknown_string_raises_value_error(self, value: str) -> None:
        with pytest.raises(ValueError):
            DroneState(value)
