from __future__ import annotations

# Standard library imports
import logging
from pathlib import Path
from typing import AsyncIterator, ClassVar, List, Optional
from uuid import UUID

# Third-party imports
import pytest

# First-party imports
from swarm_models.commands.command import Command
from swarm_models.commands.enums import CommandKind, CommandLane
from swarm_models.config.simulator.route_config import RouteConfig
from swarm_models.enums import CommandVerdict, FlightLogEntryKind
from swarm_models.simulation.commands.command_mapping_catalog import CommandMappingCatalog
from swarm_models.simulation.commands.command_reply import CommandReply
from swarm_models.simulation.commands.mavlink_command_spec import MavlinkCommandSpec
from swarm_models.simulation.flight_logs.flight_log_entry import FlightLogEntry
from swarm_service.simulation.drones.drone_service import DroneService
from swarm_service.simulation.registry.adapter_registry import AdapterRegistry
from swarm_service.simulation.routes.square_route_builder import SquareRouteBuilder
from swarm_storage.simulation.flight_logs.flight_log_store import FlightLogStore
from tests.fakes.mavlink.helpers import DRONE_IDS, MISSION_ID, OPERATOR_ID, a_flight_config, a_registered_drone
from tests.fakes.mavlink.stand_in_drone import StandInDrone
from tests.fakes.mavlink.stand_in_drones import StandInDrones


class TestDroneServiceCommands:
    COMMAND_ID = "01926f3e-0000-7000-8000-0000000000c1"
    UNKNOWN_DRONE_ID = "01926f3e-0000-7000-8000-0000000000ff"
    HOSTS: ClassVar[List[str]] = ["127.0.0.1", "localhost"]
    RETURN_HOME_ID = 20
    HOLD_ID = 193
    UNSUPPORTED_ID = 999

    @pytest.fixture
    async def services(self) -> AsyncIterator[List[DroneService]]:
        opened: List[DroneService] = []
        yield opened
        for service in opened:
            await service.close()

    def _command(self, kind: CommandKind, drone_id: Optional[str]) -> Command:
        return Command(
            id=self.COMMAND_ID,
            mission_id=MISSION_ID,
            drone_id=drone_id,
            kind=kind,
            issued_by=OPERATOR_ID,
            lane=CommandLane.SAFETY,
        )

    def _mapping(self, hold_id: int) -> CommandMappingCatalog:
        return CommandMappingCatalog(
            commands={
                CommandKind.HOLD: MavlinkCommandSpec(command_id=hold_id),
                CommandKind.RETURN_HOME: MavlinkCommandSpec(command_id=self.RETURN_HOME_ID),
            }
        )

    async def _service(
        self,
        tmp_path: Path,
        services: List[DroneService],
        stand_ins: List[StandInDrone],
        hold_id: int = HOLD_ID,
    ) -> DroneService:
        registry = AdapterRegistry(self.HOSTS)
        for index, stand_in in enumerate(stand_ins):
            registry.register(a_registered_drone(stand_in, index))
        store = FlightLogStore(str(tmp_path / "flight_log.sqlite3"))
        service = DroneService(
            registry, store, self._mapping(hold_id), SquareRouteBuilder(RouteConfig()), a_flight_config()
        )
        await service.open()
        services.append(service)
        return service

    def _entries(self, service: DroneService) -> List[FlightLogEntry]:
        return service.store.entries(UUID(MISSION_ID))

    async def test_an_unknown_drone_is_refused_logged_and_never_sent_anything(
        self,
        tmp_path: Path,
        services: List[DroneService],
        stand_in_drones: StandInDrones,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        stand_in = stand_in_drones.make()
        service = await self._service(tmp_path, services, [stand_in])

        with caplog.at_level(logging.WARNING):
            reply = await service.handle(self._command(CommandKind.RETURN_HOME, self.UNKNOWN_DRONE_ID))

        assert isinstance(reply, CommandReply)
        assert reply.verdict is CommandVerdict.REFUSED
        assert reply.reason
        warnings = [record for record in caplog.records if record.levelno == logging.WARNING]
        assert any(self.UNKNOWN_DRONE_ID in record.getMessage() for record in warnings)
        entries = self._entries(service)
        assert [entry.kind for entry in entries] == [FlightLogEntryKind.COMMAND_REFUSED]
        assert entries[0].simulated is True
        assert entries[0].mission_id == UUID(MISSION_ID)
        assert entries[0].drone_id == UUID(self.UNKNOWN_DRONE_ID)
        assert stand_in.received_commands == []

    @pytest.mark.parametrize("kind", [CommandKind.MANUAL_CONTROL, CommandKind.ABORT])
    async def test_a_kind_missing_from_the_mapping_is_refused_and_not_sent(
        self,
        kind: CommandKind,
        tmp_path: Path,
        services: List[DroneService],
        stand_in_drones: StandInDrones,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        stand_in = stand_in_drones.make()
        service = await self._service(tmp_path, services, [stand_in])

        with caplog.at_level(logging.WARNING):
            reply = await service.handle(self._command(kind, DRONE_IDS[0]))

        assert reply.verdict is CommandVerdict.REFUSED
        assert reply.reason
        assert any(record.levelno == logging.WARNING for record in caplog.records)
        assert [entry.kind for entry in self._entries(service)] == [FlightLogEntryKind.COMMAND_REFUSED]
        assert stand_in.received_commands == []

    async def test_return_home_to_a_registered_drone_is_accepted_and_sent(
        self, tmp_path: Path, services: List[DroneService], stand_in_drones: StandInDrones
    ) -> None:
        stand_in = stand_in_drones.make()
        service = await self._service(tmp_path, services, [stand_in])

        reply = await service.handle(self._command(CommandKind.RETURN_HOME, DRONE_IDS[0]))

        assert reply.verdict is CommandVerdict.ACCEPTED
        assert reply.command_id == UUID(self.COMMAND_ID)
        assert stand_in.received_commands == [self.RETURN_HOME_ID]
        entries = self._entries(service)
        assert [entry.kind for entry in entries] == [FlightLogEntryKind.COMMAND_ACCEPTED]
        assert entries[0].drone_id == UUID(DRONE_IDS[0])
        assert entries[0].simulated is True

    async def test_a_command_without_a_drone_reaches_every_registered_drone(
        self, tmp_path: Path, services: List[DroneService], stand_in_drones: StandInDrones
    ) -> None:
        stand_ins = [stand_in_drones.make() for _ in range(3)]
        service = await self._service(tmp_path, services, stand_ins)

        reply = await service.handle(self._command(CommandKind.RETURN_HOME, None))

        assert reply.verdict is CommandVerdict.ACCEPTED
        assert [stand_in.received_commands for stand_in in stand_ins] == [[self.RETURN_HOME_ID]] * 3
        entries = self._entries(service)
        assert [entry.kind for entry in entries] == [FlightLogEntryKind.COMMAND_ACCEPTED] * 3
        assert {entry.drone_id for entry in entries} == {UUID(drone_id) for drone_id in DRONE_IDS[:3]}

    async def test_a_drone_that_refuses_the_command_gives_a_refused_reply(
        self, tmp_path: Path, services: List[DroneService], stand_in_drones: StandInDrones
    ) -> None:
        stand_in = stand_in_drones.make()
        service = await self._service(tmp_path, services, [stand_in], hold_id=self.UNSUPPORTED_ID)

        reply = await service.handle(self._command(CommandKind.HOLD, DRONE_IDS[0]))

        assert reply.verdict is CommandVerdict.REFUSED
        assert reply.reason
        assert stand_in.received_commands == [self.UNSUPPORTED_ID]
        assert FlightLogEntryKind.COMMAND_ACCEPTED not in [entry.kind for entry in self._entries(service)]

    async def test_close_is_safe_twice(
        self, tmp_path: Path, services: List[DroneService], stand_in_drones: StandInDrones
    ) -> None:
        service = await self._service(tmp_path, services, [stand_in_drones.make()])
        await service.handle(self._command(CommandKind.RETURN_HOME, DRONE_IDS[0]))

        await service.close()
        await service.close()
