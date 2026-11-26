from __future__ import annotations

# Standard library imports
from functools import partial
from logging import getLogger
from pathlib import Path
from typing import ClassVar
from uuid import UUID

# First-party imports
from swarm_models.commands.command import Command
from swarm_models.commands.enums import CommandKind, CommandLane
from swarm_models.config.simulator.simulator_config import SimulatorConfig
from swarm_models.enums import CommandVerdict
from swarm_service.simulation.bus.command_endpoint import CommandEndpoint
from swarm_service.simulation.factories.drones.drone_service_factory import DroneServiceFactory
from tests.fakes.mavlink.helpers import DRONE_IDS, MISSION_ID, OPERATOR_ID, a_registered_drone
from tests.fakes.mavlink.stand_in_drone import StandInDrone


class TestCommandEndpoint:
    COMMAND_ID: ClassVar[str] = "0190a5b2-7c3e-7d4f-8a1b-2c3d4e5f7001"
    UNKNOWN_DRONE_ID: ClassVar[str] = "0190a5b2-7c3e-7d4f-8a1b-2c3d4e5f7099"
    RETURN_TO_LAUNCH: ClassVar[int] = 20

    def a_command(self, drone_id: str, kind: CommandKind = CommandKind.RETURN_HOME) -> Command:
        return Command(
            id=UUID(self.COMMAND_ID),
            mission_id=UUID(str(MISSION_ID)),
            drone_id=UUID(drone_id),
            kind=kind,
            issued_by=UUID(str(OPERATOR_ID)),
            lane=CommandLane.SAFETY,
        )

    async def test_it_delegates_a_command_to_the_service_and_returns_its_reply(
        self, stand_in_drone: StandInDrone, app_config: partial[Path]
    ) -> None:
        config = SimulatorConfig.load(app_config([a_registered_drone(stand_in_drone)]))
        service = DroneServiceFactory(config, getLogger(__name__)).create()
        await service.open()
        endpoint = CommandEndpoint(service, getLogger(__name__))

        reply = await endpoint.handle(self.a_command(DRONE_IDS[0]))
        await service.close()

        assert reply.verdict == CommandVerdict.ACCEPTED
        assert reply.command_id == UUID(self.COMMAND_ID)
        assert self.RETURN_TO_LAUNCH in stand_in_drone.received_commands

    async def test_it_returns_the_refusal_of_the_service_for_an_unknown_drone(
        self, stand_in_drone: StandInDrone, app_config: partial[Path]
    ) -> None:
        config = SimulatorConfig.load(app_config([a_registered_drone(stand_in_drone)]))
        service = DroneServiceFactory(config, getLogger(__name__)).create()
        await service.open()
        endpoint = CommandEndpoint(service, getLogger(__name__))

        reply = await endpoint.handle(self.a_command(self.UNKNOWN_DRONE_ID))
        await service.close()

        assert reply.verdict == CommandVerdict.REFUSED
        assert reply.reason
        assert stand_in_drone.received_commands == []
