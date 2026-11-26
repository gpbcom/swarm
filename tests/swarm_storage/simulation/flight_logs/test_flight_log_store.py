from __future__ import annotations

# Standard library imports
import sqlite3
from itertools import count
from pathlib import Path
from typing import ClassVar, List
from uuid import UUID

# Third-party imports
import pytest

# First-party imports
from simulator.models.enums import FlightLogEntryKind
from simulator.models.flight_logs.exceptions import (
    SEFlightLogStoreNotSimulatedError,
    SEFlightLogStoreUnwritableError,
)
from simulator.models.flight_logs.flight_log_entry import FlightLogEntry
from simulator.storage.edge.flight_log_store import FlightLogStore


class TestFlightLogStore:
    SELECT_SIMULATED: ClassVar[str] = "SELECT simulated FROM flight_log_entries"
    SELECT_COUNT: ClassVar[str] = "SELECT COUNT(*) FROM flight_log_entries"
    INSERT_ROW: ClassVar[str] = (
        "INSERT INTO flight_log_entries (mission_id, drone_id, t_us, kind, seq, detail, simulated) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)"
    )
    TIMESTAMP_MS_BITS: ClassVar[int] = 80
    FIRST_TIMESTAMP_MS: ClassVar[int] = 0x019000000000
    VERSION_7_BITS: ClassVar[int] = 7 << 76
    VARIANT_BITS: ClassVar[int] = 0b10 << 62
    DRONE_ID: ClassVar[str] = str(
        UUID(int=(FIRST_TIMESTAMP_MS << TIMESTAMP_MS_BITS) | VERSION_7_BITS | VARIANT_BITS | 1)
    )
    COUNTER: ClassVar[count[int]] = count(2)

    def a_uuid7(self) -> UUID:
        return UUID(
            int=(self.FIRST_TIMESTAMP_MS << self.TIMESTAMP_MS_BITS)
            | self.VERSION_7_BITS
            | self.VARIANT_BITS
            | next(self.COUNTER)
        )

    def an_entry(
        self, mission_id: UUID, t_us: int, kind: FlightLogEntryKind = FlightLogEntryKind.ARMED
    ) -> FlightLogEntry:
        return FlightLogEntry(mission_id=mission_id, drone_id=self.DRONE_ID, t_us=t_us, kind=kind, seq=1, detail=None)

    def test_open_creates_a_missing_folder(self, tmp_path: Path) -> None:
        path = tmp_path / "a" / "b" / "flight_log.sqlite3"
        store = FlightLogStore(str(path))
        store.open()
        store.close()
        assert path.is_file()

    def test_append_then_entries_gives_the_same_entries_back(self, tmp_path: Path) -> None:
        mission_id = self.a_uuid7()
        written = [
            self.an_entry(mission_id, 10, FlightLogEntryKind.ARMED),
            self.an_entry(mission_id, 20, FlightLogEntryKind.ROUTE_STARTED),
        ]
        store = FlightLogStore(str(tmp_path / "log.sqlite3"))
        store.open()
        for entry in written:
            store.append(entry)
        read: List[FlightLogEntry] = store.entries(mission_id)
        store.close()
        assert read == written

    def test_entries_are_ordered_by_time_then_insertion(self, tmp_path: Path) -> None:
        mission_id = self.a_uuid7()
        late = self.an_entry(mission_id, 30, FlightLogEntryKind.ROUTE_COMPLETED)
        first = self.an_entry(mission_id, 10, FlightLogEntryKind.ARMED)
        second = self.an_entry(mission_id, 10, FlightLogEntryKind.ROUTE_STARTED)
        store = FlightLogStore(str(tmp_path / "log.sqlite3"))
        store.open()
        for entry in (late, first, second):
            store.append(entry)
        read = store.entries(mission_id)
        store.close()
        assert read == [first, second, late]

    def test_every_stored_row_is_marked_simulated(self, tmp_path: Path) -> None:
        path = tmp_path / "log.sqlite3"
        mission_id = self.a_uuid7()
        store = FlightLogStore(str(path))
        store.open()
        store.append(self.an_entry(mission_id, 1))
        store.append(self.an_entry(mission_id, 2))
        store.close()
        connection = sqlite3.connect(str(path))
        rows = connection.execute(self.SELECT_SIMULATED).fetchall()
        connection.close()
        assert rows == [(1,), (1,)]

    def test_a_row_with_simulated_zero_is_refused_by_sqlite_itself(self, tmp_path: Path) -> None:
        path = tmp_path / "log.sqlite3"
        store = FlightLogStore(str(path))
        store.open()
        store.close()
        connection = sqlite3.connect(str(path))
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                self.INSERT_ROW, (str(self.a_uuid7()), self.DRONE_ID, 1, FlightLogEntryKind.ARMED.value, 1, None, 0)
            )
        connection.close()

    def test_an_entry_that_is_not_simulated_is_refused_and_not_stored(self, tmp_path: Path) -> None:
        mission_id = self.a_uuid7()
        entry = FlightLogEntry.model_construct(
            mission_id=mission_id,
            drone_id=self.DRONE_ID,
            t_us=1,
            kind=FlightLogEntryKind.ARMED,
            seq=1,
            detail=None,
            simulated=False,
        )
        store = FlightLogStore(str(tmp_path / "log.sqlite3"))
        store.open()
        with pytest.raises(SEFlightLogStoreNotSimulatedError):
            store.append(entry)
        read = store.entries(mission_id)
        store.close()
        assert read == []

    def test_another_missions_entries_are_not_returned(self, tmp_path: Path) -> None:
        mine = self.a_uuid7()
        theirs = self.a_uuid7()
        wanted = self.an_entry(mine, 1)
        store = FlightLogStore(str(tmp_path / "log.sqlite3"))
        store.open()
        store.append(wanted)
        store.append(self.an_entry(theirs, 2))
        read = store.entries(mine)
        store.close()
        assert read == [wanted]

    def test_a_path_that_is_a_folder_is_unwritable(self, tmp_path: Path) -> None:
        store = FlightLogStore(str(tmp_path))
        with pytest.raises(SEFlightLogStoreUnwritableError):
            store.open()
            store.append(self.an_entry(self.a_uuid7(), 1))
        store.close()

    def test_close_is_safe_twice(self, tmp_path: Path) -> None:
        store = FlightLogStore(str(tmp_path / "log.sqlite3"))
        store.open()
        store.close()
        store.close()

    def test_close_is_safe_before_open(self, tmp_path: Path) -> None:
        FlightLogStore(str(tmp_path / "log.sqlite3")).close()
