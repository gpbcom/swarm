from __future__ import annotations

# Standard library imports
from http import HTTPStatus
from pathlib import Path

# First-party imports
from swarm_models.enums import FlightLogEntryKind
from tests.swarm_simulator.main.helpers import (
    MISSION_ID,
    SYNTHETIC_COUNT,
    count_kind,
    flight_log_path,
    flight_log_rows,
    px4_endpoint,
    run_fly,
    synthetic_endpoints,
    write_app_config,
    write_squad_catalog,
)


class TestSquareRouteFlight:
    PX4_ROUTE_TIMEOUT_S = 600
    PX4_HEARTBEAT_TIMEOUT_S = 120
    PX4_ARM_TIMEOUT_S = 300
    PX4_FLY_TIMEOUT_S = 700.0

    def test_ten_synthetic_drones_complete_a_square_route(
        self, tmp_path: Path, simulator_script: Path, synthetic_drones: int
    ) -> None:
        catalog = write_squad_catalog(tmp_path, synthetic_endpoints(synthetic_drones))
        config = write_app_config(tmp_path, catalog)

        accepted = run_fly(config, MISSION_ID, SYNTHETIC_COUNT)

        assert accepted.status_code == HTTPStatus.ACCEPTED, accepted.text
        rows = flight_log_rows(flight_log_path(tmp_path))
        assert count_kind(rows, FlightLogEntryKind.ROUTE_COMPLETED) == SYNTHETIC_COUNT
        assert count_kind(rows, FlightLogEntryKind.ROUTE_FAILED) == 0

    def test_ten_synthetic_drones_and_one_px4_sitl_drone_all_complete_it(
        self, tmp_path: Path, simulator_script: Path, synthetic_drones: int, px4_sitl: int
    ) -> None:
        endpoints = [*synthetic_endpoints(synthetic_drones), px4_endpoint(px4_sitl)]
        catalog = write_squad_catalog(tmp_path, endpoints)
        config = write_app_config(
            tmp_path,
            catalog,
            heartbeat_timeout_s=self.PX4_HEARTBEAT_TIMEOUT_S,
            arm_timeout_s=self.PX4_ARM_TIMEOUT_S,
            route_timeout_s=self.PX4_ROUTE_TIMEOUT_S,
        )

        accepted = run_fly(config, MISSION_ID, SYNTHETIC_COUNT + 1, self.PX4_FLY_TIMEOUT_S)

        assert accepted.status_code == HTTPStatus.ACCEPTED, accepted.text
        rows = flight_log_rows(flight_log_path(tmp_path))
        assert count_kind(rows, FlightLogEntryKind.ROUTE_COMPLETED) == SYNTHETIC_COUNT + 1
