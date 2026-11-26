from __future__ import annotations

# Standard library imports
import socket
from typing import ClassVar, List

# Third-party imports
import pytest
from fastapi import FastAPI
from websockets.asyncio.client import connect
from websockets.exceptions import InvalidMessage

# First-party imports
from flight_engine.api.live.live_endpoint import LiveEndpoint
from flight_engine.api.server.live_server import LiveServer
from flight_engine.models.config.live_server_config import LiveServerConfig
from swarm_lifecycle.models.enums import RunnableStatus
from swarm_live.service.live_codec import LiveCodec
from swarm_live.service.live_hub import LiveHub


class TestLiveServer:
    HOST: ClassVar[str] = "127.0.0.1"
    STATUS_INTERVAL_S: ClassVar[float] = 0.05
    PATH: ClassVar[str] = "/v1/live"
    TIMEOUT_S: ClassVar[float] = 5.0

    def free_port(self) -> int:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
            probe.bind((self.HOST, 0))
            return int(probe.getsockname()[1])

    def a_config(self) -> LiveServerConfig:
        return LiveServerConfig(host=self.HOST, port=self.free_port(), status_interval_s=self.STATUS_INTERVAL_S)

    def a_server(self, config: LiveServerConfig) -> LiveServer:
        app = FastAPI()
        app.include_router(LiveEndpoint(LiveHub(), LiveCodec(), config).router())
        return LiveServer(app, config)

    def url(self, config: LiveServerConfig) -> str:
        return f"ws://{self.HOST}:{config.port}{self.PATH}"

    def test_the_status_interval_comes_from_the_configuration(self) -> None:
        config = self.a_config()

        assert self.a_server(config).status_interval_s == config.status_interval_s

    async def test_a_websocket_client_connects_while_the_status_is_running(self) -> None:
        config = self.a_config()
        generator = self.a_server(config).execute()
        statuses: List[RunnableStatus] = []
        connected = False
        try:
            async for status in generator:
                statuses.append(status)
                if status == RunnableStatus.RUNNING:
                    async with connect(self.url(config), open_timeout=self.TIMEOUT_S) as websocket:
                        connected = websocket.protocol is not None
                    break
        finally:
            await generator.aclose()

        assert connected
        assert all(isinstance(status, RunnableStatus) for status in statuses)

    async def test_the_port_is_freed_once_the_generator_is_closed(self) -> None:
        config = self.a_config()
        generator = self.a_server(config).execute()
        async for status in generator:
            if status == RunnableStatus.RUNNING:
                break
        await generator.aclose()

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
            probe.bind((self.HOST, config.port))

    async def test_a_closed_server_refuses_connections(self) -> None:
        config = self.a_config()
        generator = self.a_server(config).execute()
        async for status in generator:
            if status == RunnableStatus.RUNNING:
                break
        await generator.aclose()

        with pytest.raises((OSError, InvalidMessage)):
            async with connect(self.url(config), open_timeout=self.TIMEOUT_S):
                pass

    async def test_close_before_initialize_is_safe(self) -> None:
        await self.a_server(self.a_config()).close()
