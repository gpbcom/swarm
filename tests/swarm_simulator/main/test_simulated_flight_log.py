from __future__ import annotations

# Standard library imports
import sqlite3
from http import HTTPStatus
from pathlib import Path
from typing import Tuple

# Third-party imports
import pytest

# First-party imports
from swarm_models.enums import FlightLogEntryKind
from tests.swarm_simulator.main.helpers import (
    MISSION_ID,
    SYNTHETIC_COUNT,
    flight_log_path,
    flight_log_rows,
    insert_unsimulated_copy,
    kinds_of,
    run_fly,
    squad_drone_id,
    synthetic_endpoints,
    write_app_config,
    write_squad_catalog,
)

Cell = Tuple[str, int, Path, Path]


class TestSimulatedFlightLog:
    SIMULATED = 1

    @pytest.fixture
    def flown(self, tmp_path: Path, simulator_script: Path, synthetic_drones: int, nats_cell: Cell) -> Path:
        url, _, simulated_creds, _ = nats_cell
        catalog = write_squad_catalog(tmp_path, synthetic_endpoints(synthetic_drones))
        config = write_app_config(tmp_path, catalog, simulated_creds, url)
        accepted = run_fly(config, MISSION_ID, SYNTHETIC_COUNT)
        assert accepted.status_code == HTTPStatus.ACCEPTED, accepted.text
        return flight_log_path(tmp_path)

    def test_every_row_of_the_flight_log_is_marked_simulated(self, flown: Path) -> None:
        rows = flight_log_rows(flown)

        assert rows
        assert {simulated for _, _, simulated in rows} == {self.SIMULATED}

    def test_a_row_that_is_not_simulated_is_refused_by_the_database(self, flown: Path) -> None:
        with pytest.raises(sqlite3.IntegrityError):
            insert_unsimulated_copy(flown)

    def test_each_drone_logs_its_flight_in_order(self, flown: Path) -> None:
        rows = flight_log_rows(flown)

        for index in range(SYNTHETIC_COUNT):
            kinds = kinds_of(rows, squad_drone_id(index + 1))
            assert kinds[:3] == [
                FlightLogEntryKind.ROUTE_UPLOADED.value,
                FlightLogEntryKind.ARMED.value,
                FlightLogEntryKind.ROUTE_STARTED.value,
            ]
            assert kinds[-1] == FlightLogEntryKind.ROUTE_COMPLETED.value
            middle = kinds[3:-1]
            assert middle
            assert set(middle) == {FlightLogEntryKind.WAYPOINT_REACHED.value}
