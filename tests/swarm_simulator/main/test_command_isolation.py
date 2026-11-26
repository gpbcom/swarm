from __future__ import annotations

# Standard library imports
import shutil
import subprocess
import time
from pathlib import Path
from typing import AsyncIterator, Iterator, List, Tuple

# Third-party imports
import nats
import pytest
from nats.aio.client import Client

# First-party imports
from simulator.models.enums import CommandVerdict, FlightLogEntryKind, SimulatedDroneKind
from swarm_clients.shared.nats.nats_requester import NatsRequester
from swarm_models.commands.command import Command
from swarm_models.commands.enums import CommandKind, CommandLane
from swarm_models.enums import CredentialKind
from swarm_nats.models.config.nats_client_config import NatsClientConfig
from tests.infra.nats.helpers import connz_users, free_port, issuers, operator_mode_config, write_creds
from tests.infra.nats.nats_server_process import NatsServerProcess
from tests.simulator.helpers import (
    COMMAND_ID,
    ENCODING,
    HOST,
    ISSUER_ID,
    MISSION_ID,
    OPERATOR_ID,
    UNKNOWN_DRONE_ID,
    WARNING_WORD,
    Endpoint,
    flight_log_path,
    flight_log_rows,
    request_until_answered,
    squad_drone_id,
    start_serve,
    write_app_config,
    write_squad_catalog,
)

Cell = Tuple[str, int, Path, Path]


@pytest.mark.skipif(shutil.which("nats-server") is None, reason="nats-server is not installed")
class TestCommandIsolation:
    OPERATOR_NAME = "cell"
    SIMULATED_NAME = "squad-sim"
    SERVICE_NAME = "service"
    REGISTERED_ENDPOINT: Endpoint = (squad_drone_id(1), SimulatedDroneKind.SYNTHETIC, HOST, 14690, 1)
    LOG_WAIT_S = 10.0
    POLL_INTERVAL_S = 0.1
    EXIT_WAIT_S = 30.0
    SIMULATED = 1
    STDERR_NAME = "serve.stderr"

    @pytest.fixture
    def cell(self, tmp_path: Path) -> Iterator[Cell]:
        operator_issuer, account_issuer, credential_issuer = issuers()
        operator = operator_issuer.issue(self.OPERATOR_NAME)
        account = account_issuer.issue(operator, OPERATOR_ID)
        simulated = credential_issuer.issue(account, OPERATOR_ID, CredentialKind.SIMULATED, self.SIMULATED_NAME)
        service = credential_issuer.issue(account, OPERATOR_ID, CredentialKind.SERVICE, self.SERVICE_NAME)
        simulated_creds = write_creds(tmp_path / "creds", simulated, credential_issuer)
        service_creds = write_creds(tmp_path / "creds", service, credential_issuer)
        port = free_port()
        monitor_port = free_port()
        config = operator_mode_config(port, monitor_port, operator, [account], store_dir=tmp_path / "jetstream")
        server = NatsServerProcess(tmp_path, config, port)
        server.spawn()
        yield server.url, monitor_port, simulated_creds, service_creds
        server.kill()

    @pytest.fixture
    def processes(self, simulator_script: Path) -> Iterator[List[subprocess.Popen[bytes]]]:
        """Hold the ``swarm-simulator serve`` processes of a test and stop them after it."""
        started: List[subprocess.Popen[bytes]] = []
        yield started
        for process in started:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=self.EXIT_WAIT_S)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()

    def serve(self, processes: List[subprocess.Popen[bytes]], tmp_path: Path, config: Path) -> subprocess.Popen[bytes]:
        process = start_serve(config, tmp_path / self.STDERR_NAME)
        processes.append(process)
        return process

    @pytest.fixture
    async def caller(self, cell: Cell) -> AsyncIterator[Client]:
        url, _, _, service_creds = cell
        client = await nats.connect(url, user_credentials=str(service_creds))
        yield client
        await client.close()

    def command(self) -> Command:
        return Command(
            id=COMMAND_ID,
            mission_id=MISSION_ID,
            drone_id=UNKNOWN_DRONE_ID,
            kind=CommandKind.RETURN_HOME,
            issued_by=ISSUER_ID,
            lane=CommandLane.SAFETY,
        )

    def lines_with(self, path: Path, *words: str) -> List[str]:
        deadline = time.monotonic() + self.LOG_WAIT_S
        while True:
            text = path.read_text(encoding=ENCODING)
            lines = [line for line in text.splitlines() if all(word in line for word in words)]
            if lines or time.monotonic() >= deadline:
                return lines
            time.sleep(self.POLL_INTERVAL_S)

    async def test_a_command_to_a_drone_outside_the_registry_is_refused_and_logged(
        self, tmp_path: Path, cell: Cell, processes: List[subprocess.Popen[bytes]], caller: Client
    ) -> None:
        url, _, simulated_creds, service_creds = cell
        catalog = write_squad_catalog(tmp_path, [self.REGISTERED_ENDPOINT])
        config = write_app_config(tmp_path, catalog, simulated_creds, url)
        process = self.serve(processes, tmp_path, config)
        requester = NatsRequester(caller, NatsClientConfig(servers=[url], credentials_path=str(service_creds)))
        command = self.command()

        reply = await request_until_answered(requester, command, process)

        assert reply.verdict == CommandVerdict.REFUSED
        assert reply.command_id == command.id
        assert self.lines_with(tmp_path / self.STDERR_NAME, WARNING_WORD, str(UNKNOWN_DRONE_ID))
        refused = [
            (drone_id, simulated)
            for drone_id, kind, simulated in flight_log_rows(flight_log_path(tmp_path))
            if kind == FlightLogEntryKind.COMMAND_REFUSED.value
        ]
        assert refused == [(str(UNKNOWN_DRONE_ID), self.SIMULATED)]

    def test_a_serve_started_with_a_service_credential_exits_and_never_connects(
        self, tmp_path: Path, cell: Cell, processes: List[subprocess.Popen[bytes]]
    ) -> None:
        url, monitor_port, _, service_creds = cell
        catalog = write_squad_catalog(tmp_path, [self.REGISTERED_ENDPOINT])
        config = write_app_config(tmp_path, catalog, service_creds, url)

        exit_code = self.serve(processes, tmp_path, config).wait(timeout=self.EXIT_WAIT_S)

        assert exit_code != 0
        assert connz_users(monitor_port) == []
