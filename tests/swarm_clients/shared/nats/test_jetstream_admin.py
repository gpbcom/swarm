from __future__ import annotations

# Standard library imports
import asyncio
from time import monotonic
from typing import ClassVar, List

# Third-party imports
import pytest
from nats.aio.client import Client
from nats.js.api import RetentionPolicy, StorageType, StreamInfo
from nats.js.errors import NotFoundError

# First-party imports
from swarm_clients.shared.nats.jetstream_admin import JetStreamAdmin
from swarm_models.enums import StreamRetention, StreamStorage
from swarm_models.streams.stream_source import StreamSource
from swarm_models.streams.stream_spec import StreamSpec
from swarm_nats.models.bus.exceptions import SENatsStreamError


class TestJetStreamAdmin:
    STREAM_NAME: ClassVar[str] = "ADMIN_TEST"
    ORIGIN_NAME: ClassVar[str] = "ORIGIN"
    COPY_NAME: ClassVar[str] = "COPY"
    EDGE_COPY_NAME: ClassVar[str] = "EDGE_COPY"
    SUBJECT: ClassVar[str] = "admin.test.one"
    OTHER_SUBJECT: ClassVar[str] = "admin.test.two"
    ORIGIN_SUBJECTS: ClassVar[List[str]] = ["op.x.>"]
    ORIGIN_MESSAGES: ClassVar[List[str]] = ["op.x.first", "op.x.second", "op.x.third"]
    EDGE_DOMAIN: ClassVar[str] = "edge"
    EDGE_API: ClassVar[str] = "$JS.edge.API"
    SINGLE_REPLICA: ClassVar[int] = 1
    THREE_REPLICAS: ClassVar[int] = 3
    POLL_TIMEOUT_S: ClassVar[float] = 5.0
    POLL_INTERVAL_S: ClassVar[float] = 0.1

    async def delete(self, nats_client: Client, name: str) -> None:
        try:
            await nats_client.jetstream().delete_stream(name)
        except NotFoundError:
            return

    async def info(self, nats_client: Client, name: str) -> StreamInfo:
        return await nats_client.jetstream().stream_info(name)

    async def wait_for_messages(self, nats_client: Client, name: str, count: int) -> int:
        deadline = monotonic() + self.POLL_TIMEOUT_S
        messages = 0
        while monotonic() < deadline:
            messages = (await self.info(nats_client, name)).state.messages
            if messages >= count:
                return messages
            await asyncio.sleep(self.POLL_INTERVAL_S)
        return messages

    async def test_a_stream_is_created_with_its_subjects(self, nats_client: Client) -> None:
        await self.delete(nats_client, self.STREAM_NAME)
        spec = StreamSpec(name=self.STREAM_NAME, subjects=[self.SUBJECT], replicas=self.SINGLE_REPLICA)
        await JetStreamAdmin(nats_client).ensure_stream(spec)
        config = (await self.info(nats_client, self.STREAM_NAME)).config
        assert config.subjects == [self.SUBJECT]
        assert config.num_replicas == self.SINGLE_REPLICA
        assert config.storage == StorageType.FILE
        assert config.retention == RetentionPolicy.LIMITS
        await self.delete(nats_client, self.STREAM_NAME)

    @pytest.mark.parametrize(
        ("storage", "retention", "expected_storage", "expected_retention"),
        [
            (StreamStorage.MEMORY, StreamRetention.INTEREST, StorageType.MEMORY, RetentionPolicy.INTEREST),
            (StreamStorage.FILE, StreamRetention.WORK_QUEUE, StorageType.FILE, RetentionPolicy.WORK_QUEUE),
        ],
    )
    async def test_storage_and_retention_are_mapped(
        self,
        nats_client: Client,
        storage: StreamStorage,
        retention: StreamRetention,
        expected_storage: StorageType,
        expected_retention: RetentionPolicy,
    ) -> None:
        await self.delete(nats_client, self.STREAM_NAME)
        spec = StreamSpec(
            name=self.STREAM_NAME,
            subjects=[self.SUBJECT],
            replicas=self.SINGLE_REPLICA,
            storage=storage,
            retention=retention,
        )
        await JetStreamAdmin(nats_client).ensure_stream(spec)
        config = (await self.info(nats_client, self.STREAM_NAME)).config
        assert config.storage == expected_storage
        assert config.retention == expected_retention
        await self.delete(nats_client, self.STREAM_NAME)

    async def test_calling_it_again_with_one_more_subject_updates_the_stream(self, nats_client: Client) -> None:
        await self.delete(nats_client, self.STREAM_NAME)
        admin = JetStreamAdmin(nats_client)
        await admin.ensure_stream(
            StreamSpec(name=self.STREAM_NAME, subjects=[self.SUBJECT], replicas=self.SINGLE_REPLICA)
        )
        await admin.ensure_stream(
            StreamSpec(name=self.STREAM_NAME, subjects=[self.SUBJECT, self.OTHER_SUBJECT], replicas=self.SINGLE_REPLICA)
        )
        config = (await self.info(nats_client, self.STREAM_NAME)).config
        assert sorted(config.subjects or []) == [self.SUBJECT, self.OTHER_SUBJECT]
        await self.delete(nats_client, self.STREAM_NAME)

    async def test_messages_of_an_origin_reach_its_copy_in_the_same_order(self, nats_client: Client) -> None:
        await self.delete(nats_client, self.COPY_NAME)
        await self.delete(nats_client, self.ORIGIN_NAME)
        admin = JetStreamAdmin(nats_client)
        await admin.ensure_stream(
            StreamSpec(name=self.ORIGIN_NAME, subjects=self.ORIGIN_SUBJECTS, replicas=self.SINGLE_REPLICA)
        )
        await admin.ensure_stream(
            StreamSpec(
                name=self.COPY_NAME,
                replicas=self.SINGLE_REPLICA,
                sources=[StreamSource(name=self.ORIGIN_NAME)],
            )
        )
        jetstream = nats_client.jetstream()
        for subject in self.ORIGIN_MESSAGES:
            await jetstream.publish(subject, subject.encode())
        reached = await self.wait_for_messages(nats_client, self.COPY_NAME, len(self.ORIGIN_MESSAGES))
        assert reached == len(self.ORIGIN_MESSAGES)
        copied: List[str] = []
        for sequence in range(1, len(self.ORIGIN_MESSAGES) + 1):
            message = await jetstream.get_msg(self.COPY_NAME, seq=sequence)
            copied.append(message.subject)
        assert copied == self.ORIGIN_MESSAGES
        await self.delete(nats_client, self.COPY_NAME)
        await self.delete(nats_client, self.ORIGIN_NAME)

    async def test_a_source_with_a_domain_is_stored_with_the_external_api(self, nats_client: Client) -> None:
        await self.delete(nats_client, self.EDGE_COPY_NAME)
        spec = StreamSpec(
            name=self.EDGE_COPY_NAME,
            replicas=self.SINGLE_REPLICA,
            sources=[StreamSource(name=self.ORIGIN_NAME, domain=self.EDGE_DOMAIN)],
        )
        await JetStreamAdmin(nats_client).ensure_stream(spec)
        sources = (await self.info(nats_client, self.EDGE_COPY_NAME)).config.sources or []
        assert [source.name for source in sources] == [self.ORIGIN_NAME]
        assert sources[0].external is not None
        assert sources[0].external.api == self.EDGE_API
        await self.delete(nats_client, self.EDGE_COPY_NAME)

    async def test_a_replicated_stream_is_refused_by_a_single_server(self, nats_client: Client) -> None:
        await self.delete(nats_client, self.STREAM_NAME)
        spec = StreamSpec(name=self.STREAM_NAME, subjects=[self.SUBJECT], replicas=self.THREE_REPLICAS)
        with pytest.raises(SENatsStreamError):
            await JetStreamAdmin(nats_client).ensure_stream(spec)
