from __future__ import annotations

# Standard library imports
import asyncio
import time
from functools import partial
from pathlib import Path
from typing import ClassVar, Tuple
from uuid import UUID

# Third-party imports
import nats

# First-party imports
from swarm_clients.shared.nats.nats_requester import NatsRequester
from swarm_lifecycle.runnables.async_runnable import AsyncRunnable
from swarm_models.commands.command import Command
from swarm_models.commands.enums import CommandKind, CommandLane
from swarm_models.config.simulator.simulator_config import SimulatorConfig
from swarm_models.enums import CommandVerdict
from swarm_models.simulation.commands.command_reply import CommandReply
from swarm_models.subjects.operator_subjects import OperatorSubjects
from swarm_nats.models.bus.exceptions import SENatsNoResponderError, SENatsRequestDeadlineExceededError
from swarm_nats.models.config.nats_client_config import NatsClientConfig
from swarm_service.simulation.bus.command_responder import CommandResponder
from swarm_service.simulation.factories.bus.command_responder_factory import CommandResponderFactory
from tests.fakes.mavlink.helpers import MISSION_ID, OPERATOR_ID, a_registered_drone
from tests.fakes.mavlink.stand_in_drone import StandInDrone

Cell = Tuple[str, int, Path, Path]


class TestCommandResponder:
    COMMAND_EVENT: ClassVar[str] = "command"
    COMMAND_ID: ClassVar[str] = "0190a5b2-7c3e-7d4f-8a1b-2c3d4e5f7002"
    UNKNOWN_DRONE_ID: ClassVar[str] = "0190a5b2-7c3e-7d4f-8a1b-2c3d4e5f7098"
    IDEMPOTENCY_KEY: ClassVar[str] = "responder-test-1"
    REQUEST_DEADLINE_S: ClassVar[float] = 2.0
    READY_TIMEOUT_S: ClassVar[float] = 30.0
    RETRY_PAUSE_S: ClassVar[float] = 0.2

    def a_command(self, drone_id: str) -> Command:
        return Command(
            id=UUID(self.COMMAND_ID),
            mission_id=UUID(str(MISSION_ID)),
            drone_id=UUID(drone_id),
            kind=CommandKind.HOLD,
            issued_by=UUID(str(OPERATOR_ID)),
            lane=CommandLane.SAFETY,
        )

    async def ask(self, url: str, service_creds: Path, drone_id: str) -> CommandReply:
        client = await nats.connect(url, user_credentials=str(service_creds))
        requester = NatsRequester(client, NatsClientConfig(servers=[url]))
        subject = OperatorSubjects(operator_id=UUID(str(OPERATOR_ID))).mission(MISSION_ID, self.COMMAND_EVENT)
        deadline = time.monotonic() + self.READY_TIMEOUT_S
        try:
            while True:
                try:
                    return await requester.request(
                        subject,
                        self.a_command(drone_id),
                        CommandReply,
                        self.IDEMPOTENCY_KEY,
                        self.REQUEST_DEADLINE_S,
                    )
                except (SENatsNoResponderError, SENatsRequestDeadlineExceededError):
                    if time.monotonic() > deadline:
                        raise
                    await asyncio.sleep(self.RETRY_PAUSE_S)
        finally:
            await client.close()

    async def consume(self, responder: CommandResponder) -> None:
        async for _ in responder.execute():
            pass

    def test_it_is_an_async_runnable(self) -> None:
        assert issubclass(CommandResponder, AsyncRunnable)

    async def test_with_simulated_credentials_it_answers_a_command_for_an_unknown_drone_with_refused(
        self, nats_cell: Cell, stand_in_drone: StandInDrone, app_config: partial[Path]
    ) -> None:
        url, _, simulated_creds, service_creds = nats_cell
        config = SimulatorConfig.load(
            app_config([a_registered_drone(stand_in_drone)], server=url, creds=simulated_creds)
        )
        responder = CommandResponderFactory(config).create()
        task = asyncio.create_task(self.consume(responder))

        try:
            reply = await self.ask(url, service_creds, self.UNKNOWN_DRONE_ID)
        finally:
            task.cancel()
            await asyncio.gather(task, return_exceptions=True)

        assert reply.verdict == CommandVerdict.REFUSED
        assert reply.command_id == UUID(self.COMMAND_ID)
        assert reply.reason
        assert responder.client is None

    async def test_close_is_safe_before_it_connects(
        self, stand_in_drone: StandInDrone, app_config: partial[Path]
    ) -> None:
        config = SimulatorConfig.load(app_config([a_registered_drone(stand_in_drone)]))
        responder = CommandResponderFactory(config).create()

        await responder.close()

        assert responder.client is None
