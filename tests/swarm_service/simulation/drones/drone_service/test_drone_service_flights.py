from __future__ import annotations

# Standard library imports
import logging
from pathlib import Path
from typing import Iterator, List
from uuid import UUID

# Third-party imports
import pytest

# First-party imports
from services.simulator.tests.helpers import MISSION_ID, a_registered_drone
from services.simulator.tests.stand_in_drone import StandInDrone
from services.simulator.tests.stand_in_drones import StandInDrones
from simulator.clients.mavlink.mavlink_drone_client import MavlinkDroneClient
from simulator.models.config.flight_config import FlightConfig
from simulator.models.config.route_config import RouteConfig
from simulator.models.enums import FlightLogEntryKind
from simulator.models.flight_logs.flight_log_entry import FlightLogEntry
from simulator.models.flights.exceptions import SEDroneFlightTimeoutError
from simulator.models.mavlink.exceptions import SEMavlinkClientTimeoutError
from simulator.service.flights.drone_flight import DroneFlight
from simulator.service.routes.square_route_builder import SquareRouteBuilder
from simulator.storage.edge.flight_log_store import FlightLogStore
from swarm_lifecycle.models.enums import RunnableStatus

WAYPOINTS = 5
STORE_FILE = "flight_log.sqlite3"


class TestDroneFlight:
    @pytest.fixture
    def store(self, tmp_path: Path) -> Iterator[FlightLogStore]:
        flight_log_store = FlightLogStore(str(tmp_path / STORE_FILE))
        flight_log_store.open()
        yield flight_log_store
        flight_log_store.close()

    @pytest.fixture
    def config(self) -> FlightConfig:
        return FlightConfig(heartbeat_timeout_s=1.0, arm_timeout_s=2.0, route_timeout_s=1.0, status_interval_s=0.1)

    def a_flight(self, stand_in: StandInDrone, store: FlightLogStore, config: FlightConfig) -> DroneFlight:
        drone = a_registered_drone(stand_in)
        return DroneFlight(
            drone,
            UUID(str(MISSION_ID)),
            MavlinkDroneClient(drone, config),
            SquareRouteBuilder(RouteConfig()),
            store,
            config,
        )

    def entries(self, store: FlightLogStore) -> List[FlightLogEntry]:
        return store.entries(UUID(str(MISSION_ID)))

    async def test_execute_yields_its_status_then_executed(
        self, stand_in_drone: StandInDrone, store: FlightLogStore, config: FlightConfig
    ) -> None:
        flight = self.a_flight(stand_in_drone, store, config)
        statuses = [status async for status in flight.execute()]
        assert statuses[-1] == RunnableStatus.EXECUTED
        assert set(statuses[:-1]) <= {RunnableStatus.INITIALISING, RunnableStatus.RUNNING}

    async def test_the_outcome_is_completed_with_five_waypoints(
        self, stand_in_drone: StandInDrone, store: FlightLogStore, config: FlightConfig
    ) -> None:
        flight = self.a_flight(stand_in_drone, store, config)
        async for _ in flight.execute():
            pass
        assert flight.outcome is not None
        assert flight.outcome.completed is True
        assert flight.outcome.waypoints_reached == WAYPOINTS
        assert flight.outcome.drone_id == flight.drone.drone_id

    async def test_the_flight_log_follows_the_flight_in_order_and_is_simulated(
        self, stand_in_drone: StandInDrone, store: FlightLogStore, config: FlightConfig
    ) -> None:
        flight = self.a_flight(stand_in_drone, store, config)
        async for _ in flight.execute():
            pass
        entries = self.entries(store)
        expected = [
            FlightLogEntryKind.ROUTE_UPLOADED,
            FlightLogEntryKind.ARMED,
            FlightLogEntryKind.ROUTE_STARTED,
            *[FlightLogEntryKind.WAYPOINT_REACHED] * WAYPOINTS,
            FlightLogEntryKind.ROUTE_COMPLETED,
        ]
        assert [entry.kind for entry in entries] == expected
        reached = [entry.seq for entry in entries if entry.kind == FlightLogEntryKind.WAYPOINT_REACHED]
        assert reached == list(range(1, WAYPOINTS + 1))
        assert all(entry.simulated is True for entry in entries)

    async def test_a_stalled_drone_gives_the_timeout_error_and_an_incomplete_outcome(
        self,
        stand_in_drones: StandInDrones,
        store: FlightLogStore,
        config: FlightConfig,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        stalled = stand_in_drones.make(stall_after_seq=2)
        flight = self.a_flight(stalled, store, config)
        with caplog.at_level(logging.ERROR), pytest.raises(SEDroneFlightTimeoutError):
            async for _ in flight.execute():
                pass
        assert flight.outcome is not None
        assert flight.outcome.completed is False
        entries = self.entries(store)
        assert entries[-1].kind == FlightLogEntryKind.ROUTE_FAILED
        assert entries[-1].detail == SEMavlinkClientTimeoutError.__name__
        assert FlightLogEntryKind.ROUTE_COMPLETED not in [entry.kind for entry in entries]
        assert all(entry.simulated is True for entry in entries)
        assert any(record.levelno == logging.ERROR for record in caplog.records)

    async def test_a_silent_drone_fails_in_initialize_the_same_way(
        self, stand_in_drones: StandInDrones, store: FlightLogStore, config: FlightConfig
    ) -> None:
        silent = stand_in_drones.make(silent=True)
        flight = self.a_flight(silent, store, config)
        with pytest.raises(SEDroneFlightTimeoutError):
            async for _ in flight.execute():
                pass
        assert flight.outcome is not None
        assert flight.outcome.completed is False
        assert [entry.kind for entry in self.entries(store)] == [FlightLogEntryKind.ROUTE_FAILED]
