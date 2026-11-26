from __future__ import annotations

# Standard library imports
import asyncio
import signal
import socket
from pathlib import Path
from typing import ClassVar

# Third-party imports
import pytest
from websockets.asyncio.client import connect

pytest.importorskip("swarm_core")

# First-party imports
from swarm_api.v1.flight.flight_engine_router import FlightEngineRouter
from swarm_lifecycle.runnables.async_runnable import AsyncRunnable
from swarm_models.config.flight_engine.flight_engine_config import FlightEngineConfig
from swarm_models.config.flight_engine.live_server_config import LiveServerConfig
from swarm_nats.models.bus.exceptions import SENatsConnectionError
from swarm_nats.models.config.nats_client_config import NatsClientConfig
from swarm_service.flight.engine.flight_engine_server import FlightEngineServer
from swarm_service.flight.factories.engine.flight_engine_server_factory import FlightEngineServerFactory


class TestFlightEngineServer:
    HOST: ClassVar[str] = "127.0.0.1"
    PATH: ClassVar[str] = "/v1/live"
    MISSIONS_NAME: ClassVar[str] = "missions.yaml"
    STATES: ClassVar[Path] = (
        Path(__file__).resolve().parents[4]
        / "backend"
        / "apps"
        / "flight-engine"
        / "conf"
        / "catalogs"
        / "drone_states.yaml"
    )
    ENCODING: ClassVar[str] = "utf-8"
    READY_TIMEOUT_S: ClassVar[float] = 15.0
    STOP_TIMEOUT_S: ClassVar[float] = 15.0
    POLL_S: ClassVar[float] = 0.05
    STATUS_INTERVAL_S: ClassVar[float] = 0.05
    CONNECT_TIMEOUT_S: ClassVar[float] = 1.0

    def free_port(self) -> int:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
            probe.bind((self.HOST, 0))
            return int(probe.getsockname()[1])

    def a_config(self, tmp_path: Path, nats_url: str) -> FlightEngineConfig:
        missions = tmp_path / self.MISSIONS_NAME
        missions.write_text("missions: []\n", encoding=self.ENCODING)
        return FlightEngineConfig(
            status_interval_s=self.STATUS_INTERVAL_S,
            missions_catalog_path=str(missions),
            drone_states_catalog_path=str(self.STATES),
            nats=NatsClientConfig(servers=[nats_url], connect_timeout_s=self.CONNECT_TIMEOUT_S),
            live=LiveServerConfig(host=self.HOST, port=self.free_port(), status_interval_s=self.STATUS_INTERVAL_S),
        )

    def a_server(self, config: FlightEngineConfig) -> FlightEngineServer:
        router = FlightEngineRouter(config)
        return FlightEngineServerFactory(config, router.application(), router.hub, router.codec).create()

    async def consume(self, server: FlightEngineServer) -> None:
        async for _ in server.execute():
            pass

    async def test_the_factory_builds_an_async_runnable(self, tmp_path: Path, nats_url: str) -> None:
        server = self.a_server(self.a_config(tmp_path, nats_url))

        assert isinstance(server, FlightEngineServer)
        assert isinstance(server, AsyncRunnable)

    async def test_the_socket_is_served_after_the_engine_ends_and_cancelling_stops_both(
        self, tmp_path: Path, nats_url: str
    ) -> None:
        config = self.a_config(tmp_path, nats_url)
        task = asyncio.create_task(self.consume(self.a_server(config)))
        url = f"ws://{self.HOST}:{config.live.port}{self.PATH}"
        connected = False
        deadline = asyncio.get_running_loop().time() + self.READY_TIMEOUT_S
        while not connected and asyncio.get_running_loop().time() < deadline:
            try:
                async with connect(url, open_timeout=self.POLL_S * 10):
                    connected = True
            except OSError:
                await asyncio.sleep(self.POLL_S)

        task.cancel()
        await asyncio.gather(task, return_exceptions=True)

        assert connected
        assert task.done()

    async def test_a_failed_engine_stops_the_server_and_is_raised(self, tmp_path: Path) -> None:
        config = self.a_config(tmp_path, f"nats://{self.HOST}:{self.free_port()}")

        with pytest.raises(SENatsConnectionError):
            await asyncio.wait_for(self.consume(self.a_server(config)), timeout=self.STOP_TIMEOUT_S)

    async def test_the_handlers_of_the_stop_signals_are_put_back_when_it_ends(self, tmp_path: Path) -> None:
        before = [signal.getsignal(stop) for stop in FlightEngineServer.STOP_SIGNALS]
        config = self.a_config(tmp_path, f"nats://{self.HOST}:{self.free_port()}")

        with pytest.raises(SENatsConnectionError):
            await asyncio.wait_for(self.consume(self.a_server(config)), timeout=self.STOP_TIMEOUT_S)

        assert [signal.getsignal(stop) for stop in FlightEngineServer.STOP_SIGNALS] == before
