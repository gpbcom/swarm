from __future__ import annotations

from typing import ClassVar, Dict
from uuid import UUID

import pytest
from pydantic import JsonValue, ValidationError

from simulator.models.enums import FlightLogEntryKind
from simulator.models.flight_logs.exceptions import (
    SEFlightLogEntryInvalidDetail,
    SEFlightLogEntryInvalidDroneId,
    SEFlightLogEntryInvalidKind,
    SEFlightLogEntryInvalidMissionId,
    SEFlightLogEntryInvalidSeq,
    SEFlightLogEntryInvalidTUs,
    SEFlightLogEntryNotSimulated,
)
from simulator.models.flight_logs.flight_log_entry import FlightLogEntry


class TestFlightLogEntry:
    MISSION_ID: ClassVar[str] = "01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e5f"
    DRONE_ID: ClassVar[str] = "01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e60"
    UUID4: ClassVar[str] = "3f2b8c1e-5d4a-4b6c-9e7f-1a2b3c4d5e6f"
    VALID: ClassVar[Dict[str, JsonValue]] = {
        "mission_id": MISSION_ID,
        "drone_id": DRONE_ID,
        "t_us": 1_500_000,
        "kind": FlightLogEntryKind.WAYPOINT_REACHED.value,
        "seq": 3,
        "detail": "waypoint 3",
        "simulated": True,
    }

    def build(self, **changes: JsonValue) -> FlightLogEntry:
        values: Dict[str, JsonValue] = dict(self.VALID)
        values.update(changes)
        return FlightLogEntry.model_validate(values)

    def test_defaults(self) -> None:
        entry = FlightLogEntry(mission_id=UUID(self.MISSION_ID), t_us=0, kind=FlightLogEntryKind.ARMED)
        assert entry.drone_id is None
        assert entry.seq is None
        assert entry.detail is None
        assert entry.simulated is True

    def test_full_valid_construction(self) -> None:
        entry = self.build()
        assert entry.mission_id == UUID(self.MISSION_ID)
        assert entry.drone_id == UUID(self.DRONE_ID)
        assert entry.t_us == 1_500_000
        assert entry.kind == FlightLogEntryKind.WAYPOINT_REACHED
        assert entry.seq == 3
        assert entry.detail == "waypoint 3"
        assert entry.simulated is True

    @pytest.mark.parametrize(
        ("name", "default"),
        [("drone_id", None), ("seq", None), ("detail", None), ("simulated", True)],
    )
    def test_none_becomes_the_default(self, name: str, default: JsonValue) -> None:
        assert getattr(self.build(**{name: None}), name) == default

    @pytest.mark.parametrize(
        ("name", "value", "error"),
        [
            ("mission_id", None, SEFlightLogEntryInvalidMissionId),
            ("mission_id", UUID4, SEFlightLogEntryInvalidMissionId),
            ("mission_id", "not-a-uuid", SEFlightLogEntryInvalidMissionId),
            ("mission_id", 7, SEFlightLogEntryInvalidMissionId),
            ("drone_id", UUID4, SEFlightLogEntryInvalidDroneId),
            ("drone_id", "not-a-uuid", SEFlightLogEntryInvalidDroneId),
            ("drone_id", True, SEFlightLogEntryInvalidDroneId),
            ("t_us", None, SEFlightLogEntryInvalidTUs),
            ("t_us", -1, SEFlightLogEntryInvalidTUs),
            ("t_us", True, SEFlightLogEntryInvalidTUs),
            ("t_us", 1.5, SEFlightLogEntryInvalidTUs),
            ("t_us", "1", SEFlightLogEntryInvalidTUs),
            ("kind", None, SEFlightLogEntryInvalidKind),
            ("kind", "teleport", SEFlightLogEntryInvalidKind),
            ("kind", 3, SEFlightLogEntryInvalidKind),
            ("seq", -1, SEFlightLogEntryInvalidSeq),
            ("seq", True, SEFlightLogEntryInvalidSeq),
            ("seq", 1.5, SEFlightLogEntryInvalidSeq),
            ("seq", "1", SEFlightLogEntryInvalidSeq),
            ("detail", "", SEFlightLogEntryInvalidDetail),
            ("detail", "   ", SEFlightLogEntryInvalidDetail),
            ("detail", 5, SEFlightLogEntryInvalidDetail),
            ("detail", True, SEFlightLogEntryInvalidDetail),
            ("simulated", False, SEFlightLogEntryNotSimulated),
        ],
    )
    def test_rejects_bad_values(self, name: str, value: JsonValue, error: type[Exception]) -> None:
        with pytest.raises(error):
            self.build(**{name: value})

    def test_a_flight_log_entry_that_is_not_simulated_is_refused(self) -> None:
        with pytest.raises(SEFlightLogEntryNotSimulated):
            FlightLogEntry(
                mission_id=UUID(self.MISSION_ID),
                t_us=0,
                kind=FlightLogEntryKind.ARMED,
                simulated=False,
            )

    @pytest.mark.parametrize("kind", list(FlightLogEntryKind))
    def test_every_kind_is_accepted_as_a_member_or_as_its_value(self, kind: FlightLogEntryKind) -> None:
        assert self.build(kind=kind.value).kind == kind
        assert self.build(kind=kind).kind == kind

    def test_the_detail_is_stripped(self) -> None:
        assert self.build(detail="  reached  ").detail == "reached"

    def test_an_entry_for_the_whole_squad_has_no_drone(self) -> None:
        assert self.build(drone_id=None).drone_id is None

    def test_a_time_of_zero_is_accepted(self) -> None:
        assert self.build(t_us=0).t_us == 0

    def test_rejects_unknown_keys(self) -> None:
        with pytest.raises(ValidationError):
            self.build(extra=1)

    def test_assigning_a_field_of_a_built_entry_is_refused(self) -> None:
        entry = self.build()
        with pytest.raises(ValidationError):
            entry.t_us = 2

    def test_round_trip(self) -> None:
        entry = self.build()
        assert FlightLogEntry.model_validate(entry.model_dump()) == entry
        assert FlightLogEntry.model_validate_json(entry.model_dump_json()) == entry

    def test_a_round_trip_keeps_the_entry_simulated(self) -> None:
        entry = self.build()
        assert FlightLogEntry.model_validate(entry.model_dump()).simulated is True
        assert FlightLogEntry.model_validate_json(entry.model_dump_json()).simulated is True
