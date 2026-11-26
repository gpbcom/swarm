from __future__ import annotations

# Standard library imports
import logging
from pathlib import Path
from typing import ClassVar, List
from uuid import UUID

# Third-party imports
import pytest

# First-party imports
from swarm_lifecycle.models.enums import RunnableStatus
from swarm_models.commands.enums import CommandKind
from swarm_models.config.simulator.flight_config import FlightConfig
from swarm_models.config.simulator.route_config import RouteConfig
from swarm_models.simulation.commands.command_mapping_catalog import CommandMappingCatalog
from swarm_models.simulation.commands.mavlink_command_spec import MavlinkCommandSpec
from swarm_service.simulation.drones.drone_service import DroneService
from swarm_service.simulation.flights.squad_flight import SquadFlight
from swarm_service.simulation.registry.adapter_registry import AdapterRegistry
from swarm_service.simulation.routes.square_route_builder import SquareRouteBuilder
from swarm_storage.simulation.flight_logs.flight_log_store import FlightLogStore
from tests.fakes.mavlink.helpers import MISSION_ID, a_registered_drone
from tests.fakes.mavlink.stand_in_drone import StandInDrone
from tests.fakes.mavlink.stand_in_drones import StandInDrones

STORE_FILE = "flight_log.sqlite3"
SQUAD_SIZE = 3


class TestSquadFlight:
    HOSTS: ClassVar[List[str]] = ["127.0.0.1", "localhost"]
    RETURN_HOME_ID: ClassVar[int] = 20
    MAPPING: ClassVar[CommandMappingCatalog] = CommandMappingCatalog(
        commands={CommandKind.RETURN_HOME: MavlinkCommandSpec(command_id=RETURN_HOME_ID)}
    )

    @pytest.fixture
    def config(self) -> FlightConfig:
        return FlightConfig(heartbeat_timeout_s=1.0, arm_timeout_s=2.0, route_timeout_s=1.0, status_interval_s=0.1)

    def a_squad(self, stand_ins: List[StandInDrone], tmp_path: Path, config: FlightConfig) -> SquadFlight:
        registry = AdapterRegistry(self.HOSTS)
        for index, stand_in in enumerate(stand_ins):
            registry.register(a_registered_drone(stand_in, index))
        store = FlightLogStore(str(tmp_path / STORE_FILE))
        service = DroneService(registry, store, self.MAPPING, SquareRouteBuilder(RouteConfig()), config)
        return SquadFlight(service, UUID(str(MISSION_ID)), config.status_interval_s)

    async def test_a_squad_of_three_completes_every_flight(
        self, stand_in_drones: StandInDrones, tmp_path: Path, config: FlightConfig
    ) -> None:
        stand_ins = [stand_in_drones.make() for _ in range(SQUAD_SIZE)]
        squad = self.a_squad(stand_ins, tmp_path, config)
        statuses = [status async for status in squad.execute()]
        assert statuses[-1] == RunnableStatus.EXECUTED
        assert set(statuses[:-1]) <= {RunnableStatus.INITIALISING, RunnableStatus.RUNNING}
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
