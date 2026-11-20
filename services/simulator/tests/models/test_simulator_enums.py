from __future__ import annotations

from enum import StrEnum
from typing import ClassVar, Dict, List

import pytest

from simulator.models.enums import (
    CommandVerdict,
    FlightLogEntryKind,
    SimulatedDroneKind,
    SimulatorCommandName,
)


class TestSimulatorEnums:
    ENUMS: ClassVar[List[type[StrEnum]]] = [
        SimulatedDroneKind,
        FlightLogEntryKind,
        CommandVerdict,
        SimulatorCommandName,
    ]
    MEMBERS: ClassVar[Dict[type[StrEnum], Dict[str, str]]] = {
        SimulatedDroneKind: {"SYNTHETIC": "synthetic", "PX4_SITL": "px4_sitl"},
        FlightLogEntryKind: {
            "ROUTE_UPLOADED": "route_uploaded",
            "ARMED": "armed",
            "ROUTE_STARTED": "route_started",
            "WAYPOINT_REACHED": "waypoint_reached",
            "ROUTE_COMPLETED": "route_completed",
            "ROUTE_FAILED": "route_failed",
            "COMMAND_ACCEPTED": "command_accepted",
            "COMMAND_REFUSED": "command_refused",
        },
        CommandVerdict: {"ACCEPTED": "accepted", "REFUSED": "refused"},
        SimulatorCommandName: {"SERVE": "serve", "FLY": "fly"},
    }

    @pytest.mark.parametrize("enum", ENUMS)
    def test_each_enum_is_a_string_enum(self, enum: type[StrEnum]) -> None:
        assert issubclass(enum, StrEnum)

    @pytest.mark.parametrize("enum", ENUMS)
    def test_each_enum_has_exactly_its_members(self, enum: type[StrEnum]) -> None:
        assert {member.name: member.value for member in enum} == self.MEMBERS[enum]

    @pytest.mark.parametrize("enum", ENUMS)
    def test_no_value_holds_a_hyphen(self, enum: type[StrEnum]) -> None:
        assert all("-" not in member.value for member in enum)

    @pytest.mark.parametrize("enum", ENUMS)
    def test_every_value_is_lower_snake_case(self, enum: type[StrEnum]) -> None:
        assert all(member.value == member.value.lower() and " " not in member.value for member in enum)

    @pytest.mark.parametrize("enum", ENUMS)
    def test_a_value_finds_its_member(self, enum: type[StrEnum]) -> None:
        assert all(enum(member.value) is member for member in enum)

    @pytest.mark.parametrize("enum", ENUMS)
    def test_each_enum_declares_unique_values(self, enum: type[StrEnum]) -> None:
        assert len({member.value for member in enum}) == len(list(enum))
        assert enum.__members__.keys() == {member.name for member in enum}
