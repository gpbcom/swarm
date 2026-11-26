from __future__ import annotations

# Standard library imports
import asyncio
import socket
from functools import partial
from pathlib import Path
from typing import ClassVar, Tuple

# Third-party imports
import pytest
from fastapi import FastAPI

# First-party imports
from swarm_models.config.simulator.simulator_config import SimulatorConfig
from swarm_models.simulation.credentials.exceptions import (
    SESimulatedCredentialsNotSimulatedError,
    SESimulatedCredentialsUnreadableError,
)
from swarm_nats.models.bus.exceptions import SENatsConnectionError
from swarm_service.simulation.factories.bus.command_responder_factory import CommandResponderFactory
from swarm_service.simulation.servers.simulator_server import SimulatorServer
from swarm_web.models.config.rest_config import RestConfig
from tests.fakes.mavlink.helpers import a_registered_drone
from tests.fakes.mavlink.stand_in_drone import StandInDrone
from tests.infra.nats.helpers import connz_users, free_port
from tests.swarm_service.simulation.servers.held_rest_server_factory import HeldRestServerFactory

Cell = Tuple[str, int, Path, Path]


class TestSimulatorServer:
    HOST: ClassVar[str] = "127.0.0.1"
    MISSING_CREDS: ClassVar[str] = "missing.creds"
    STATUS_INTERVAL_S: ClassVar[float] = 0.05
    TIMEOUT_S: ClassVar[float] = 20.0
    POLL_S: ClassVar[float] = 0.05

    def a_server(self, config: SimulatorConfig, servers: HeldRestServerFactory) -> SimulatorServer:
        return SimulatorServer(config, CommandResponderFactory(config), servers, self.STATUS_INTERVAL_S)

    def held_servers(self) -> HeldRestServerFactory:
        rest = RestConfig(host=self.HOST, port=free_port(), status_interval_s=self.STATUS_INTERVAL_S)
        return HeldRestServerFactory(FastAPI(), rest)

    def answers(self, port: int) -> bool:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
            return probe.connect_ex((self.HOST, port)) == 0

    async def consume(self, server: SimulatorServer) -> None:
        async for _ in server.execute():
            pass

    async def until(self, deadline: float) -> None:
        assert asyncio.get_running_loop().time() < deadline, "The simulator server did not get ready in time."
        await asyncio.sleep(self.POLL_S)

    async def test_service_credentials_stop_the_start_before_anything_connects_or_serves(
        self, nats_cell: Cell, stand_in_drone: StandInDrone, app_config: partial[Path]
    ) -> None:
        url, monitor_port, _, service_creds = nats_cell
        config = SimulatorConfig.load(app_config([a_registered_drone(stand_in_drone)], server=url, creds=service_creds))
        servers = self.held_servers()

        with pytest.raises(SESimulatedCredentialsNotSimulatedError):
            await asyncio.wait_for(self.consume(self.a_server(config, servers)), timeout=self.TIMEOUT_S)

        assert servers.built == []
        assert connz_users(monitor_port) == []

    async def test_an_unreadable_credentials_file_stops_the_start(
        self, stand_in_drone: StandInDrone, app_config: partial[Path], tmp_path: Path
    ) -> None:
        drones = [a_registered_drone(stand_in_drone)]
        config = SimulatorConfig.load(app_config(drones, creds=tmp_path / self.MISSING_CREDS))
        servers = self.held_servers()

        with pytest.raises(SESimulatedCredentialsUnreadableError):
            await asyncio.wait_for(self.consume(self.a_server(config, servers)), timeout=self.TIMEOUT_S)

        assert servers.built == []

    async def test_a_responder_that_cannot_reach_nats_stops_the_server_and_is_raised(
        self, nats_cell: Cell, stand_in_drone: StandInDrone, app_config: partial[Path]
    ) -> None:
        _, _, simulated_creds, _ = nats_cell
        unreachable = f"nats://{self.HOST}:{free_port()}"
        drones = [a_registered_drone(stand_in_drone)]
        config = SimulatorConfig.load(app_config(drones, server=unreachable, creds=simulated_creds))
        servers = self.held_servers()

        with pytest.raises(SENatsConnectionError):
            await asyncio.wait_for(self.consume(self.a_server(config, servers)), timeout=self.TIMEOUT_S)

        assert len(servers.built) == 1
        assert servers.built[0].server is None
        assert not self.answers(servers.config.port)

    async def test_the_end_of_the_server_cancels_the_responder(
        self, nats_cell: Cell, stand_in_drone: StandInDrone, app_config: partial[Path]
    ) -> None:
        url, monitor_port, simulated_creds, _ = nats_cell
        drones = [a_registered_drone(stand_in_drone)]
        config = SimulatorConfig.load(app_config(drones, server=url, creds=simulated_creds))
        servers = self.held_servers()
        task = asyncio.create_task(self.consume(self.a_server(config, servers)))
        deadline = asyncio.get_running_loop().time() + self.TIMEOUT_S
        while not (connz_users(monitor_port) and servers.built and self.answers(servers.config.port)):
            assert not task.done(), "The simulator server stopped before it was ready."
            await self.until(deadline)
        uvicorn_server = servers.built[0].server
        assert uvicorn_server is not None

        uvicorn_server.should_exit = True
        await asyncio.wait_for(task, timeout=self.TIMEOUT_S)

        assert connz_users(monitor_port) == []
        assert not self.answers(servers.config.port)

    async def test_cancelling_it_stops_the_server_and_the_responder(
        self, nats_cell: Cell, stand_in_drone: StandInDrone, app_config: partial[Path]
    ) -> None:
        url, monitor_port, simulated_creds, _ = nats_cell
        drones = [a_registered_drone(stand_in_drone)]
        config = SimulatorConfig.load(app_config(drones, server=url, creds=simulated_creds))
        servers = self.held_servers()
        task = asyncio.create_task(self.consume(self.a_server(config, servers)))
        deadline = asyncio.get_running_loop().time() + self.TIMEOUT_S
        while not (connz_users(monitor_port) and servers.built and self.answers(servers.config.port)):
            assert not task.done(), "The simulator server stopped before it was ready."
            await self.until(deadline)

        task.cancel()
        await asyncio.gather(task, return_exceptions=True)

        assert connz_users(monitor_port) == []
        assert not self.answers(servers.config.port)
