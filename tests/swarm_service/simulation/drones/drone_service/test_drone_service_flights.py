from __future__ import annotations

# Standard library imports
import logging
from pathlib import Path
from typing import AsyncIterator, ClassVar, List
from uuid import UUID

# Third-party imports
import pytest

# First-party imports
from swarm_models.commands.enums import CommandKind
from swarm_models.config.simulator.flight_config import FlightConfig
from swarm_models.config.simulator.route_config import RouteConfig
from swarm_models.enums import FlightLogEntryKind
from swarm_models.mavlink.exceptions import SEMavlinkClientTimeoutError
from swarm_models.simulation.commands.command_mapping_catalog import CommandMappingCatalog
from swarm_models.simulation.commands.mavlink_command_spec import MavlinkCommandSpec
from swarm_models.simulation.flight_logs.flight_log_entry import FlightLogEntry
from swarm_models.simulation.flights.exceptions import SEDroneFlightTimeoutError
from swarm_models.simulation.registry.exceptions import SEAdapterRegistryUnknownDroneError
from swarm_models.simulation.registry.registered_drone import RegisteredDrone
from swarm_service.simulation.drones.drone_service import DroneService
from swarm_service.simulation.registry.adapter_registry import AdapterRegistry
from swarm_service.simulation.routes.square_route_builder import SquareRouteBuilder
from swarm_storage.simulation.flight_logs.flight_log_store import FlightLogStore
from tests.fakes.mavlink.helpers import MISSION_ID, a_registered_drone
from tests.fakes.mavlink.stand_in_drone import StandInDrone
from tests.fakes.mavlink.stand_in_drones import StandInDrones

WAYPOINTS = 5
STORE_FILE = "flight_log.sqlite3"


class TestDroneServiceFlights:
    HOSTS: ClassVar[List[str]] = ["127.0.0.1", "localhost"]
    RETURN_HOME_ID: ClassVar[int] = 20
    MAPPING: ClassVar[CommandMappingCatalog] = CommandMappingCatalog(
        commands={CommandKind.RETURN_HOME: MavlinkCommandSpec(command_id=RETURN_HOME_ID)}
    )

    @pytest.fixture
    def config(self) -> FlightConfig:
        return FlightConfig(heartbeat_timeout_s=1.0, arm_timeout_s=2.0, route_timeout_s=1.0, status_interval_s=0.1)

    @pytest.fixture
    async def services(self) -> AsyncIterator[List[DroneService]]:
        opened: List[DroneService] = []
        yield opened
        for service in opened:
            await service.close()

    async def a_service(
        self, tmp_path: Path, services: List[DroneService], drones: List[RegisteredDrone], config: FlightConfig
    ) -> DroneService:
        registry = AdapterRegistry(self.HOSTS)
        for drone in drones:
            registry.register(drone)
        store = FlightLogStore(str(tmp_path / STORE_FILE))
        service = DroneService(registry, store, self.MAPPING, SquareRouteBuilder(RouteConfig()), config)
        await service.open()
        services.append(service)
        return service

    def entries(self, service: DroneService) -> List[FlightLogEntry]:
        return service.store.entries(UUID(str(MISSION_ID)))

    async def test_the_outcome_is_completed_with_five_waypoints(
        self, tmp_path: Path, services: List[DroneService], stand_in_drone: StandInDrone, config: FlightConfig
    ) -> None:
        drone = a_registered_drone(stand_in_drone)
        service = await self.a_service(tmp_path, services, [drone], config)

        outcome = await service.fly(drone, UUID(str(MISSION_ID)))

        assert outcome.completed is True
        assert outcome.waypoints_reached == WAYPOINTS
        assert outcome.drone_id == drone.drone_id
        assert service.outcomes[drone.drone_id] == outcome

    async def test_the_flight_log_follows_the_flight_in_order_and_is_simulated(
        self, tmp_path: Path, services: List[DroneService], stand_in_drone: StandInDrone, config: FlightConfig
    ) -> None:
        drone = a_registered_drone(stand_in_drone)
        service = await self.a_service(tmp_path, services, [drone], config)

        await service.fly(drone, UUID(str(MISSION_ID)))

        entries = self.entries(service)
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
        tmp_path: Path,
        services: List[DroneService],
        stand_in_drones: StandInDrones,
        config: FlightConfig,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        drone = a_registered_drone(stand_in_drones.make(stall_after_seq=2))
        service = await self.a_service(tmp_path, services, [drone], config)

        with caplog.at_level(logging.ERROR), pytest.raises(SEDroneFlightTimeoutError):
            await service.fly(drone, UUID(str(MISSION_ID)))

        outcome = service.outcomes[drone.drone_id]
        assert outcome.completed is False
        assert outcome.waypoints_reached == 2
        entries = self.entries(service)
        assert entries[-1].kind == FlightLogEntryKind.ROUTE_FAILED
        assert entries[-1].detail == SEMavlinkClientTimeoutError.__name__
        assert FlightLogEntryKind.ROUTE_COMPLETED not in [entry.kind for entry in entries]
        assert all(entry.simulated is True for entry in entries)
        assert any(record.levelno == logging.ERROR for record in caplog.records)

    async def test_a_silent_drone_fails_before_its_route_the_same_way(
        self, tmp_path: Path, services: List[DroneService], stand_in_drones: StandInDrones, config: FlightConfig
    ) -> None:
        drone = a_registered_drone(stand_in_drones.make(silent=True))
        service = await self.a_service(tmp_path, services, [drone], config)

        with pytest.raises(SEDroneFlightTimeoutError):
            await service.fly(drone, UUID(str(MISSION_ID)))

        assert service.outcomes[drone.drone_id].completed is False
        assert [entry.kind for entry in self.entries(service)] == [FlightLogEntryKind.ROUTE_FAILED]

    async def test_a_drone_outside_the_registry_never_flies(
        self, tmp_path: Path, services: List[DroneService], stand_in_drone: StandInDrone, config: FlightConfig
    ) -> None:
        service = await self.a_service(tmp_path, services, [], config)

        with pytest.raises(SEAdapterRegistryUnknownDroneError):
            await service.fly(a_registered_drone(stand_in_drone), UUID(str(MISSION_ID)))

        assert stand_in_drone.received_commands == []
        assert self.entries(service) == []
