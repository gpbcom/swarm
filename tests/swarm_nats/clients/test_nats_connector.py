from __future__ import annotations

# Standard library imports
import socket
import time

# Third-party imports
import pytest

# First-party imports
from swarm_nats.clients.nats_connector import NatsConnector
from swarm_nats.models.bus.exceptions import SENatsConnectionError
from swarm_nats.models.config.nats_client_config import NatsClientConfig


class TestNatsConnector:
    LOCALHOST = "127.0.0.1"
    CONNECT_TIMEOUT_S = 0.5
    MAX_FAILURE_S = 5.0
    MISSING_CREDENTIALS = "/nonexistent/swarm/missing.creds"

    def free_url(self) -> str:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
            probe.bind((self.LOCALHOST, 0))
            port: int = probe.getsockname()[1]
        return f"nats://{self.LOCALHOST}:{port}"

    async def test_connecting_to_a_server_gives_a_connected_client(self, nats_url: str) -> None:
        connector = NatsConnector(NatsClientConfig(servers=[nats_url]))
        client = await connector.connect()
        assert client.is_connected
        await connector.disconnect(client)

    async def test_disconnect_leaves_the_client_closed(self, nats_url: str) -> None:
        connector = NatsConnector(NatsClientConfig(servers=[nats_url]))
        client = await connector.connect()
        await connector.disconnect(client)
        assert client.is_closed

    async def test_a_port_with_no_server_is_refused_quickly(self) -> None:
        config = NatsClientConfig(servers=[self.free_url()], connect_timeout_s=self.CONNECT_TIMEOUT_S)
        started = time.monotonic()
        with pytest.raises(SENatsConnectionError):
            await NatsConnector(config).connect()
        assert time.monotonic() - started < self.MAX_FAILURE_S

    async def test_a_credentials_file_that_does_not_exist_is_refused(self, nats_url: str) -> None:
        config = NatsClientConfig(
            servers=[nats_url],
            credentials_path=self.MISSING_CREDENTIALS,
            connect_timeout_s=self.CONNECT_TIMEOUT_S,
        )
        with pytest.raises(SENatsConnectionError):
            await NatsConnector(config).connect()
