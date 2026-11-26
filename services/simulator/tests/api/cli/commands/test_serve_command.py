from __future__ import annotations

# Standard library imports
import asyncio
import logging
import signal
import subprocess
import sys
import time
from functools import partial
from pathlib import Path
from typing import ClassVar, Iterator, Tuple
from uuid import UUID

# Third-party imports
import nats
import pytest

# First-party imports
from services.simulator.tests.helpers import MISSION_ID, OPERATOR_ID, a_registered_drone
from services.simulator.tests.stand_in_drone import StandInDrone
from simulator.api.cli.commands.serve_command import ServeCommand
from simulator.api.factories.serve.serve_command_factory import ServeCommandFactory
from simulator.models.commands.command_reply import CommandReply
from simulator.models.config.simulator_config import SimulatorConfig
from simulator.models.enums import CommandVerdict, SimulatorCommandName
from swarm_lifecycle.runnables.runnable import Runnable
from swarm_models.commands.command import Command
from swarm_models.commands.enums import CommandKind, CommandLane
from swarm_nats.clients.nats_requester import NatsRequester
from swarm_nats.models.bus.exceptions import SENatsNoResponderError, SENatsRequestDeadlineExceededError
from swarm_nats.models.config.nats_client_config import NatsClientConfig
from swarm_nats.models.subjects.operator_subjects import OperatorSubjects
from tests.infra.nats.helpers import connz_users

Cell = Tuple[str, int, Path, Path]
Served = Tuple[subprocess.Popen[bytes], str, Path]


class TestServeCommand:
    SCRIPT_NAME: ClassVar[str] = "swarm-simulator"
    CONFIG_FLAG: ClassVar[str] = "--config"
    COMMAND_EVENT: ClassVar[str] = "command"
    COMMAND_ID: ClassVar[str] = "0190a5b2-7c3e-7d4f-8a1b-2c3d4e5f7002"
    UNKNOWN_DRONE_ID: ClassVar[str] = "0190a5b2-7c3e-7d4f-8a1b-2c3d4e5f7098"
    IDEMPOTENCY_KEY: ClassVar[str] = "serve-test-1"
    LOG_NAME: ClassVar[str] = "serve.log"
    REQUEST_DEADLINE_S: ClassVar[float] = 2.0
    READY_TIMEOUT_S: ClassVar[float] = 30.0
    EXIT_TIMEOUT_S: ClassVar[float] = 20.0
    RETRY_PAUSE_S: ClassVar[float] = 0.2
    EXIT_OK: ClassVar[int] = 0
    EXIT_REFUSED_CREDENTIALS: ClassVar[int] = 3

    @pytest.fixture
    def served(
        self, nats_cell: Cell, stand_in_drone: StandInDrone, app_config: partial[Path], tmp_path: Path
    ) -> Iterator[Served]:
        url, _, simulated_creds, _ = nats_cell
        config = app_config([a_registered_drone(stand_in_drone)], server=url, creds=simulated_creds)
        log = (tmp_path / self.LOG_NAME).open("wb")
        script = Path(sys.executable).parent / self.SCRIPT_NAME
        process = subprocess.Popen(
            [str(script), SimulatorCommandName.SERVE, self.CONFIG_FLAG, str(config)],
            cwd=tmp_path,
            stdout=log,
            stderr=log,
        )
        yield process, url, nats_cell[3]
        if process.poll() is None:
            process.kill()
        process.wait()
        log.close()

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
        while True:
            try:
                reply = await requester.request(
                    subject,
                    self.a_command(drone_id),
                    CommandReply,
                    self.IDEMPOTENCY_KEY,
                    self.REQUEST_DEADLINE_S,
                )
            except (SENatsNoResponderError, SENatsRequestDeadlineExceededError):
                if time.monotonic() > deadline:
                    await client.close()
                    raise
                await asyncio.sleep(self.RETRY_PAUSE_S)
                continue
            await client.close()
            return reply

    def test_it_is_a_runnable(self) -> None:
        assert issubclass(ServeCommand, Runnable)

    def test_service_credentials_give_exit_code_three_and_nothing_connects(
        self,
        nats_cell: Cell,
        stand_in_drone: StandInDrone,
        app_config: partial[Path],
        caplog: pytest.LogCaptureFixture,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        url, monitor_port, _, service_creds = nats_cell
        config = SimulatorConfig.load(app_config([a_registered_drone(stand_in_drone)], server=url, creds=service_creds))
        command = ServeCommandFactory(config).create()

        with caplog.at_level(logging.ERROR):
            command.execute()

        assert command.exit_code == self.EXIT_REFUSED_CREDENTIALS
        assert any(record.levelno == logging.ERROR for record in caplog.records)
        assert capsys.readouterr().out.strip()
        assert connz_users(monitor_port) == []

    def test_an_unreadable_credentials_file_gives_exit_code_three(
        self, nats_cell: Cell, stand_in_drone: StandInDrone, app_config: partial[Path], tmp_path: Path
    ) -> None:
        url, monitor_port, _, _ = nats_cell
        config = SimulatorConfig.load(
            app_config([a_registered_drone(stand_in_drone)], server=url, creds=tmp_path / "missing.creds")
        )
        command = ServeCommandFactory(config).create()

        command.execute()

        assert command.exit_code == self.EXIT_REFUSED_CREDENTIALS
        assert connz_users(monitor_port) == []

    async def test_simulated_credentials_answer_a_command_for_an_unknown_drone_with_refused(
        self, served: Served
    ) -> None:
        _, url, service_creds = served

        reply = await self.ask(url, service_creds, self.UNKNOWN_DRONE_ID)

        assert reply.verdict == CommandVerdict.REFUSED
        assert reply.command_id == UUID(self.COMMAND_ID)
        assert reply.reason

    async def test_it_exits_zero_on_sigterm(self, served: Served) -> None:
        process, url, service_creds = served
        await self.ask(url, service_creds, self.UNKNOWN_DRONE_ID)

        process.send_signal(signal.SIGTERM)

        assert process.wait(timeout=self.EXIT_TIMEOUT_S) == self.EXIT_OK
