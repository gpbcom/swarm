from __future__ import annotations

# Standard library imports
import socket

# Third-party imports
import httpx
import pytest

# First-party imports
from swarm_lifecycle.models.enums import RunnableStatus
from swarm_models.rest.problems.problem import Problem
from swarm_web.models.config.rest_config import RestConfig
from swarm_web.rest.rest_app_builder import RestAppBuilder
from swarm_web.rest.rest_server import RestServer


class TestRestServer:
    HOST = "127.0.0.1"
    STATUS_INTERVAL_S = 0.05
    OPENAPI_PATH = "/v1/openapi.json"
    TITLE = "Server test"
    VERSION = "1.0.0"
    TIMEOUT_S = 5.0

    def free_port(self) -> int:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
            probe.bind((self.HOST, 0))
            return int(probe.getsockname()[1])

    def a_config(self) -> RestConfig:
        return RestConfig(host=self.HOST, port=self.free_port(), status_interval_s=self.STATUS_INTERVAL_S)

    def a_server(self, config: RestConfig) -> RestServer:
        app = RestAppBuilder().build(self.TITLE, self.VERSION, [], Problem, Problem.MEDIA_TYPE)
        return RestServer(app, config)

    def test_the_status_interval_comes_from_the_configuration(self) -> None:
        config = self.a_config()
        assert self.a_server(config).status_interval_s == config.status_interval_s

    async def test_the_app_is_served_while_the_status_is_running(self) -> None:
        config = self.a_config()
        url = f"http://{self.HOST}:{config.port}{self.OPENAPI_PATH}"
        generator = self.a_server(config).execute()
        status_code = 0
        try:
            async for status in generator:
                if status == RunnableStatus.RUNNING:
                    async with httpx.AsyncClient(timeout=self.TIMEOUT_S) as client:
                        status_code = (await client.get(url)).status_code
                    break
        except httpx.HTTPError:
            await generator.aclose()
            raise
        await generator.aclose()
        assert status_code == 200

    async def test_the_port_is_released_once_the_generator_is_closed(self) -> None:
        config = self.a_config()
        url = f"http://{self.HOST}:{config.port}{self.OPENAPI_PATH}"
        generator = self.a_server(config).execute()
        async for status in generator:
            if status == RunnableStatus.RUNNING:
                break
        await generator.aclose()
        async with httpx.AsyncClient(timeout=self.TIMEOUT_S) as client:
            with pytest.raises(httpx.ConnectError):
                await client.get(url)

    async def test_close_before_initialize_is_safe(self) -> None:
        await self.a_server(self.a_config()).close()
