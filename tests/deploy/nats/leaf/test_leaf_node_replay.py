from __future__ import annotations

import asyncio
import shutil
from pathlib import Path
from string import Template
from typing import ClassVar, List, Optional
from uuid import UUID

import pytest
from nats.aio.client import Client
from nats.js.api import StreamInfo

# First-party imports
from swarm_nats.clients.jetstream_admin import JetStreamAdmin
from swarm_nats.clients.nats_connector import NatsConnector
from swarm_nats.models.config.nats_client_config import NatsClientConfig
from swarm_nats.models.enums import CredentialKind
from swarm_nats.models.streams.stream_source import StreamSource
from swarm_nats.models.streams.stream_spec import StreamSpec
from swarm_nats.models.subjects.operator_subjects import OperatorSubjects
from tests.deploy.nats.helpers import free_port, issuers, operator_mode_config, write_creds
from tests.deploy.nats.leaf.link_proxy import LinkProxy
from tests.deploy.nats.nats_server_process import NatsServerProcess


@pytest.mark.skipif(shutil.which("nats-server") is None, reason="nats-server is not installed")
class TestLeafNodeReplay:
    OPERATOR_ID: ClassVar[UUID] = UUID("0190a5b2-7c3e-7d4f-8a1b-2c3d4e5f6a7b")
    CUT_DURATION_S: ClassVar[float] = 60.0
    FIRST_BATCH: ClassVar[int] = 10
    TOTAL: ClassVar[int] = 20
    FIRST_SYNC_TIMEOUT_S: ClassVar[float] = 30.0
    REPLAY_TIMEOUT_S: ClassVar[float] = 60.0
    POLL_INTERVAL_S: ClassVar[float] = 0.5
    EDGE_STREAM: ClassVar[str] = "EDGE_BUFFER"
    CORE_STREAM: ClassVar[str] = "FLEET_FROM_EDGE"
    EDGE_DOMAIN: ClassVar[str] = "edge"
    CORE_DOMAIN: ClassVar[str] = "cell"
    EVENT: ClassVar[str] = "position"
    LEAF_CONFIG: ClassVar[Template] = Template(
        "server_name: edge\n"
        "host: 127.0.0.1\n"
        "port: $port\n"
        'jetstream { store_dir: "$store_dir", domain: edge }\n'
        "leafnodes {\n"
        '  remotes: [ { url: "nats-leaf://127.0.0.1:$proxy_port", credentials: "$credentials" } ]\n'
        "}\n"
    )

    ############################
    # Internal Helpers Methods #
    ############################

    async def _connect(self, url: str, credentials: Optional[str] = None) -> Client:
        config = NatsClientConfig(servers=[url], credentials_path=credentials)
        return await NatsConnector(config).connect()

    async def _hub_info(self, hub: Client) -> StreamInfo:
        return await hub.jetstream().stream_info(self.CORE_STREAM)

    async def _wait_for_count(self, hub: Client, expected: int, timeout_s: float) -> int:
        deadline = asyncio.get_running_loop().time() + timeout_s
        count = 0
        while asyncio.get_running_loop().time() < deadline:
            count = (await self._hub_info(hub)).state.messages
            if count >= expected:
                return count
            await asyncio.sleep(self.POLL_INTERVAL_S)
        return count

    async def _publish(self, leaf: Client, subject: str, first: int, last: int) -> None:
        stream = leaf.jetstream()
        for number in range(first, last + 1):
            await stream.publish(subject, str(number).encode())

    async def _read_bodies(self, hub: Client, total: int) -> List[str]:
        stream = hub.jetstream()
        bodies: List[str] = []
        for sequence in range(1, total + 1):
            message = await stream.get_msg(self.CORE_STREAM, seq=sequence)
            bodies.append(message.data.decode())
        return bodies

    async def _cleanup(
        self, clients: List[Optional[Client]], proxy: LinkProxy, servers: List[NatsServerProcess]
    ) -> None:
        for client in clients:
            if client is not None:
                await client.close()
        await proxy.close()
        for server in servers:
            server.kill()

    ############################
    # Publicly Exposed Methods #
    ############################

    async def test_a_leaf_node_cut_for_one_minute_replays_its_messages_in_order(self, tmp_path: Path) -> None:
        operator_issuer, account_issuer, credential_issuer = issuers()
        operator = operator_issuer.issue("cell")
        account = account_issuer.issue(operator, self.OPERATOR_ID)
        edge = credential_issuer.issue(account, self.OPERATOR_ID, CredentialKind.EDGE, "edge-a")
        service = credential_issuer.issue(account, self.OPERATOR_ID, CredentialKind.SERVICE, "service-a")
        edge_creds = write_creds(tmp_path, edge, credential_issuer)
        service_creds = write_creds(tmp_path, service, credential_issuer)
        hub_port = free_port()
        hub_monitor_port = free_port()
        hub_leafnode_port = free_port()
        leaf_port = free_port()
        (tmp_path / "hub").mkdir()
        (tmp_path / "leaf").mkdir()
        hub_server = NatsServerProcess(
            tmp_path / "hub",
            operator_mode_config(
                hub_port,
                hub_monitor_port,
                operator,
                [account],
                store_dir=tmp_path / "hub" / "js",
                domain=self.CORE_DOMAIN,
                leafnode_port=hub_leafnode_port,
            ),
            hub_port,
        )
        proxy = LinkProxy(hub_leafnode_port)
        proxy_port = await proxy.listen()
        leaf_server = NatsServerProcess(
            tmp_path / "leaf",
            self.LEAF_CONFIG.substitute(
                port=leaf_port,
                store_dir=tmp_path / "leaf" / "js",
                proxy_port=proxy_port,
                credentials=edge_creds,
            ),
            leaf_port,
        )
        hub: Optional[Client] = None
        leaf: Optional[Client] = None
        try:
            hub_server.spawn()
            leaf_server.spawn()
            hub = await self._connect(hub_server.url, str(service_creds))
            leaf = await self._connect(leaf_server.url)
            subject = OperatorSubjects(operator_id=self.OPERATOR_ID).fleet(self.EVENT)
            await JetStreamAdmin(leaf).ensure_stream(StreamSpec(name=self.EDGE_STREAM, subjects=[subject], replicas=1))
            await JetStreamAdmin(hub).ensure_stream(
                StreamSpec(
                    name=self.CORE_STREAM,
                    subjects=[],
                    replicas=1,
                    sources=[StreamSource(name=self.EDGE_STREAM, domain=self.EDGE_DOMAIN)],
                )
            )
            await self._publish(leaf, subject, 1, self.FIRST_BATCH)
            assert await self._wait_for_count(hub, self.FIRST_BATCH, self.FIRST_SYNC_TIMEOUT_S) == self.FIRST_BATCH
            await proxy.cut()
            await self._publish(leaf, subject, self.FIRST_BATCH + 1, self.TOTAL)
            await asyncio.sleep(self.CUT_DURATION_S)
            assert (await self._hub_info(hub)).state.messages == self.FIRST_BATCH
            await proxy.restore()
            assert await self._wait_for_count(hub, self.TOTAL, self.REPLAY_TIMEOUT_S) == self.TOTAL
            bodies = await self._read_bodies(hub, self.TOTAL)
            assert bodies == [str(number) for number in range(1, self.TOTAL + 1)]
        except Exception:
            await self._cleanup([leaf, hub], proxy, [leaf_server, hub_server])
            raise
        await self._cleanup([leaf, hub], proxy, [leaf_server, hub_server])
