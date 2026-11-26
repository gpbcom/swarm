from __future__ import annotations

# Standard library imports
from typing import ClassVar, Dict, List
from uuid import UUID

# Third-party imports
import pytest
from pydantic import JsonValue, ValidationError

# First-party imports
from flight_engine.models.missions.drone_entry import DroneEntry
from flight_engine.models.missions.exceptions import (
    SEInvalidMissionEntryException,
    SEMissionEntryDuplicateDrone,
    SEMissionEntryDuplicateSystemId,
    SEMissionEntryInvalidDrones,
    SEMissionEntryInvalidMavlinkHost,
    SEMissionEntryInvalidMavlinkPort,
    SEMissionEntryInvalidMissionId,
    SEMissionEntryInvalidOperatorId,
)
from flight_engine.models.missions.mission_entry import MissionEntry


class TestMissionEntry:
    OPERATOR_ID: ClassVar[str] = "01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e5e"
    MISSION_ID: ClassVar[str] = "01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e5f"
    UUID4: ClassVar[str] = "3f2b8c1e-5d4a-4b6c-9e7f-1a2b3c4d5e6f"
    FIRST: ClassVar[Dict[str, JsonValue]] = {"system_id": 1, "drone_id": "01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e61"}
    SECOND: ClassVar[Dict[str, JsonValue]] = {"system_id": 2, "drone_id": "01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e62"}
    SAME_SYSTEM_ID: ClassVar[Dict[str, JsonValue]] = {**SECOND, "system_id": 1}
    SAME_DRONE: ClassVar[Dict[str, JsonValue]] = {**SECOND, "drone_id": FIRST["drone_id"]}
    VALID: ClassVar[Dict[str, JsonValue]] = {
        "operator_id": OPERATOR_ID,
        "mission_id": MISSION_ID,
        "mavlink_host": "127.0.0.1",
        "mavlink_port": 14550,
        "drones": [FIRST, SECOND],
    }
    REQUIRED: ClassVar[List[str]] = ["operator_id", "mission_id", "mavlink_port", "drones"]

    def build(self, **changes: JsonValue) -> MissionEntry:
        values: Dict[str, JsonValue] = dict(self.VALID)
        values.update(changes)
        return MissionEntry.model_validate(values)

    def test_defaults(self) -> None:
        values: Dict[str, JsonValue] = dict(self.VALID)
        del values["mavlink_host"]
        entry = MissionEntry.model_validate(values)
        assert entry.mavlink_host == "0.0.0.0"

    def test_full_valid_construction(self) -> None:
        entry = self.build()
        assert entry.operator_id == UUID(self.OPERATOR_ID)
        assert entry.mission_id == UUID(self.MISSION_ID)
        assert entry.mavlink_host == "127.0.0.1"
        assert entry.mavlink_port == 14550
        assert [drone.system_id for drone in entry.drones] == [1, 2]
        assert all(isinstance(drone, DroneEntry) for drone in entry.drones)

    def test_none_becomes_the_default(self) -> None:
        assert self.build(mavlink_host=None).mavlink_host == "0.0.0.0"

    @pytest.mark.parametrize("name", REQUIRED)
    def test_none_is_refused_for_a_required_field(self, name: str) -> None:
        with pytest.raises(SEInvalidMissionEntryException):
            self.build(**{name: None})

    @pytest.mark.parametrize(
        ("name", "value", "error"),
        [
            ("operator_id", UUID4, SEMissionEntryInvalidOperatorId),
            ("operator_id", "not-a-uuid", SEMissionEntryInvalidOperatorId),
            ("operator_id", 7, SEMissionEntryInvalidOperatorId),
            ("operator_id", True, SEMissionEntryInvalidOperatorId),
            ("mission_id", UUID4, SEMissionEntryInvalidMissionId),
            ("mission_id", "not-a-uuid", SEMissionEntryInvalidMissionId),
            ("mission_id", 7, SEMissionEntryInvalidMissionId),
            ("mavlink_host", "", SEMissionEntryInvalidMavlinkHost),
            ("mavlink_host", "   ", SEMissionEntryInvalidMavlinkHost),
            ("mavlink_host", 3, SEMissionEntryInvalidMavlinkHost),
            ("mavlink_host", True, SEMissionEntryInvalidMavlinkHost),
            ("mavlink_port", 0, SEMissionEntryInvalidMavlinkPort),
            ("mavlink_port", 65536, SEMissionEntryInvalidMavlinkPort),
            ("mavlink_port", True, SEMissionEntryInvalidMavlinkPort),
            ("mavlink_port", 1.5, SEMissionEntryInvalidMavlinkPort),
            ("mavlink_port", "14550", SEMissionEntryInvalidMavlinkPort),
            ("drones", "drones", SEMissionEntryInvalidDrones),
            ("drones", 3, SEMissionEntryInvalidDrones),
            ("drones", {"system_id": 1}, SEMissionEntryInvalidDrones),
            ("drones", [3], SEMissionEntryInvalidDrones),
            ("drones", [FIRST, SAME_SYSTEM_ID], SEMissionEntryDuplicateSystemId),
            ("drones", [FIRST, SAME_DRONE], SEMissionEntryDuplicateDrone),
        ],
    )
    def test_rejects_bad_values(self, name: str, value: JsonValue, error: type[Exception]) -> None:
        with pytest.raises(error):
            self.build(**{name: value})

    def test_rejects_unknown_keys(self) -> None:
        with pytest.raises(ValidationError):
            self.build(colour="red")

    def test_round_trip(self) -> None:
        entry = self.build()
        assert MissionEntry.model_validate(entry.model_dump()) == entry

    @pytest.mark.parametrize("port", [1, 65535])
    def test_the_bounds_of_the_port_are_accepted(self, port: int) -> None:
        assert self.build(mavlink_port=port).mavlink_port == port

    def test_the_duplicate_errors_are_model_errors(self) -> None:
        assert issubclass(SEMissionEntryDuplicateSystemId, SEInvalidMissionEntryException)
        assert issubclass(SEMissionEntryDuplicateDrone, SEInvalidMissionEntryException)
