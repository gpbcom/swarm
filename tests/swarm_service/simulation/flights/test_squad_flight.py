from __future__ import annotations

# Standard library imports
import logging
from pathlib import Path
from typing import List
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
from simulator.service.flights.drone_flight import DroneFlight
from simulator.service.flights.squad_flight import SquadFlight
from simulator.service.routes.square_route_builder import SquareRouteBuilder
from simulator.storage.edge.flight_log_store import FlightLogStore
from swarm_lifecycle.models.enums import RunnableStatus

STORE_FILE = "flight_log.sqlite3"
SQUAD_SIZE = 3


class TestSquadFlight:
    @pytest.fixture
    def config(self) -> FlightConfig:
        return FlightConfig(heartbeat_timeout_s=1.0, arm_timeout_s=2.0, route_timeout_s=1.0, status_interval_s=0.1)

    def a_squad(self, stand_ins: List[StandInDrone], tmp_path: Path, config: FlightConfig) -> SquadFlight:
        store = FlightLogStore(str(tmp_path / STORE_FILE))
        builder = SquareRouteBuilder(RouteConfig())
        flights: List[DroneFlight] = []
        for index, stand_in in enumerate(stand_ins):
            drone = a_registered_drone(stand_in, index)
            flights.append(
                DroneFlight(drone, UUID(str(MISSION_ID)), MavlinkDroneClient(drone, config), builder, store, config)
            )
        return SquadFlight(flights, store, config.status_interval_s)

    async def test_a_squad_of_three_completes_every_flight(
        self, stand_in_drones: StandInDrones, tmp_path: Path, config: FlightConfig
    ) -> None:
        stand_ins = [stand_in_drones.make() for _ in range(SQUAD_SIZE)]
        squad = self.a_squad(stand_ins, tmp_path, config)
        statuses = [status async for status in squad.execute()]
        assert statuses[-1] == RunnableStatus.EXECUTED
        assert len(squad.outcomes) == SQUAD_SIZE
        assert squad.all_completed is True

    async def test_a_stalled_drone_makes_the_squad_incomplete_without_raising(
        self,
        stand_in_drones: StandInDrones,
        tmp_path: Path,
        config: FlightConfig,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        stand_ins = [stand_in_drones.make(), stand_in_drones.make(stall_after_seq=2), stand_in_drones.make()]
        squad = self.a_squad(stand_ins, tmp_path, config)
        with caplog.at_level(logging.WARNING):
            statuses = [status async for status in squad.execute()]
        assert statuses[-1] == RunnableStatus.EXECUTED
        assert squad.all_completed is False
        completed = [outcome.completed for outcome in squad.outcomes]
        assert completed.count(True) == SQUAD_SIZE - 1
        assert completed.count(False) == 1
        assert any(record.levelno == logging.WARNING for record in caplog.records)

    async def test_a_squad_without_flights_is_not_all_completed(self, tmp_path: Path, config: FlightConfig) -> None:
        squad = self.a_squad([], tmp_path, config)
        async for _ in squad.execute():
            pass
        assert squad.outcomes == []
        assert squad.all_completed is False
