from __future__ import annotations

# Standard library imports
import asyncio
import logging
from logging import getLogger
from typing import ClassVar, List
from uuid import UUID

# Third-party imports
import pytest
from live_stand_in_socket import LiveStandInSocket

# First-party imports
from swarm_lifecycle.models.enums import RunnableStatus  # isort: skip
from swarm_live.api.factories.live.live_session_factory import LiveSessionFactory  # isort: skip
from swarm_live.api.live.live_session import LiveSession  # isort: skip
from swarm_models.live.session.live_session_config import LiveSessionConfig  # isort: skip
from swarm_live.service.hub_live_source import HubLiveSource  # isort: skip
from swarm_live.service.live_codec import LiveCodec  # isort: skip
from swarm_live.service.live_hub import LiveHub  # isort: skip
from swarm_models.enums import LiveOperation, LiveTopicKind
from swarm_models.live.live_subscription import LiveSubscription


class TestLiveSession:
    MISSION_ID: ClassVar[UUID] = UUID("01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e5f")
    OTHER_MISSION_ID: ClassVar[UUID] = UUID("01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e70")
    SLOW_SEND_S: ClassVar[float] = 0.2
    PUBLISH_COUNT: ClassVar[int] = 50
    PUBLISH_EVERY_S: ClassVar[float] = 0.01
    FIRST_STATUSES: ClassVar[List[RunnableStatus]] = [RunnableStatus.INITIALISING, RunnableStatus.RUNNING]

    def a_subscription(self, mission_id: UUID) -> LiveSubscription:
        topic = LiveSubscription.topic_of(mission_id, LiveTopicKind.SQUAD)
        return LiveSubscription(op=LiveOperation.SUBSCRIBE, topic=topic)

    async def drain(self, session: LiveSession, statuses: List[RunnableStatus]) -> None:
        async for status in session.execute():
            statuses.append(status)

    async def wait_for_watchers(self, hub: LiveHub, topic: str, count: int) -> None:
        async with asyncio.timeout(2.0):
            while hub.watchers(topic) < count:
                await asyncio.sleep(0.005)

    async def test_a_session_sends_the_frames_published_to_its_topic(
        self,
        stand_in_socket: LiveStandInSocket,
        hub: LiveHub,
        source: HubLiveSource,
        codec: LiveCodec,
        config: LiveSessionConfig,
    ) -> None:
        subscription = self.a_subscription(self.MISSION_ID)
        session = LiveSession(stand_in_socket, source, codec, config)
        task = asyncio.create_task(self.drain(session, []))
        stand_in_socket.feed(codec.encode_subscription(subscription))
        await self.wait_for_watchers(hub, subscription.topic, 1)
        hub.publish(subscription.topic, b"frame-1")
        await stand_in_socket.wait_for_sent(1)
        stand_in_socket.disconnect()
        await asyncio.wait_for(task, timeout=2.0)
        assert stand_in_socket.sent == [b"frame-1"]
        assert session.sent == 1

    async def test_a_frame_for_another_topic_is_not_sent(
        self,
        stand_in_socket: LiveStandInSocket,
        hub: LiveHub,
        source: HubLiveSource,
        codec: LiveCodec,
        config: LiveSessionConfig,
    ) -> None:
        subscription = self.a_subscription(self.MISSION_ID)
        other = self.a_subscription(self.OTHER_MISSION_ID)
        session = LiveSession(stand_in_socket, source, codec, config)
        task = asyncio.create_task(self.drain(session, []))
        stand_in_socket.feed(codec.encode_subscription(subscription))
        await self.wait_for_watchers(hub, subscription.topic, 1)
        hub.publish(other.topic, b"other")
        await asyncio.sleep(0.1)
        stand_in_socket.disconnect()
        await asyncio.wait_for(task, timeout=2.0)
        assert stand_in_socket.sent == []

    async def test_a_slow_client_skips_frames_and_ends_on_the_latest(
        self, hub: LiveHub, source: HubLiveSource, codec: LiveCodec, config: LiveSessionConfig
    ) -> None:
        slow_socket = LiveStandInSocket(send_delay_s=self.SLOW_SEND_S)
        subscription = self.a_subscription(self.MISSION_ID)
        session = LiveSession(slow_socket, source, codec, config)
        task = asyncio.create_task(self.drain(session, []))
        slow_socket.feed(codec.encode_subscription(subscription))
        await self.wait_for_watchers(hub, subscription.topic, 1)
        for index in range(self.PUBLISH_COUNT):
            hub.publish(subscription.topic, str(index).encode())
            await asyncio.sleep(self.PUBLISH_EVERY_S)
        last = str(self.PUBLISH_COUNT - 1).encode()
        async with asyncio.timeout(3.0):
            while not slow_socket.sent or slow_socket.sent[-1] != last:
                await asyncio.sleep(0.01)
        slow_socket.disconnect()
        await asyncio.wait_for(task, timeout=3.0)
        indexes = [int(data) for data in slow_socket.sent]
        assert 1 <= len(slow_socket.sent) < self.PUBLISH_COUNT // 3
        assert indexes == sorted(set(indexes))
        assert slow_socket.sent[-1] == last
        assert session.sent == len(slow_socket.sent)

    async def test_a_disconnect_ends_execute_with_the_source_left(
        self,
        stand_in_socket: LiveStandInSocket,
        hub: LiveHub,
        source: HubLiveSource,
        codec: LiveCodec,
        config: LiveSessionConfig,
    ) -> None:
        subscription = self.a_subscription(self.MISSION_ID)
        session = LiveSession(stand_in_socket, source, codec, config)
        statuses: List[RunnableStatus] = []
        task = asyncio.create_task(self.drain(session, statuses))
        stand_in_socket.feed(codec.encode_subscription(subscription))
        await self.wait_for_watchers(hub, subscription.topic, 1)
        stand_in_socket.disconnect()
        await asyncio.wait_for(task, timeout=2.0)
        assert hub.watchers(subscription.topic) == 0
        assert statuses[-1] is RunnableStatus.EXECUTED

    async def test_execute_yields_runnable_statuses(
        self,
        stand_in_socket: LiveStandInSocket,
        source: HubLiveSource,
        codec: LiveCodec,
        config: LiveSessionConfig,
    ) -> None:
        session = LiveSession(stand_in_socket, source, codec, config)
        statuses: List[RunnableStatus] = []
        task = asyncio.create_task(self.drain(session, statuses))
        await asyncio.sleep(0.2)
        stand_in_socket.disconnect()
        await asyncio.wait_for(task, timeout=2.0)
        assert statuses
        assert all(isinstance(status, RunnableStatus) for status in statuses)
        assert statuses[0] in self.FIRST_STATUSES
        assert RunnableStatus.RUNNING in statuses
        assert statuses[-1] is RunnableStatus.EXECUTED
        assert session.status is RunnableStatus.EXECUTED

    async def test_an_unreadable_message_is_logged_and_ignored(
        self,
        stand_in_socket: LiveStandInSocket,
        hub: LiveHub,
        source: HubLiveSource,
        codec: LiveCodec,
        config: LiveSessionConfig,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        subscription = self.a_subscription(self.MISSION_ID)
        logger = getLogger("test_live_session")
        session = LiveSession(stand_in_socket, source, codec, config, logger)
        with caplog.at_level(logging.WARNING, logger="test_live_session"):
            task = asyncio.create_task(self.drain(session, []))
            stand_in_socket.feed(b"not msgpack at all")
            stand_in_socket.feed(codec.encode_subscription(subscription))
            await self.wait_for_watchers(hub, subscription.topic, 1)
            hub.publish(subscription.topic, b"still-alive")
            await stand_in_socket.wait_for_sent(1)
            stand_in_socket.disconnect()
            await asyncio.wait_for(task, timeout=2.0)
        assert stand_in_socket.sent == [b"still-alive"]
        assert any(record.levelno == logging.WARNING for record in caplog.records)

    async def test_a_session_built_by_the_factory_runs_until_the_client_leaves(
        self,
        stand_in_socket: LiveStandInSocket,
        source: HubLiveSource,
        codec: LiveCodec,
        config: LiveSessionConfig,
    ) -> None:
        session = LiveSessionFactory(stand_in_socket, source, codec, config).create()
        stand_in_socket.disconnect()
        async with asyncio.timeout(2.0):
            statuses = [status async for status in session.execute()]
        assert statuses[-1] is RunnableStatus.EXECUTED

    async def test_a_session_may_join_several_topics_on_one_socket(
        self,
        stand_in_socket: LiveStandInSocket,
        hub: LiveHub,
        source: HubLiveSource,
        codec: LiveCodec,
        config: LiveSessionConfig,
    ) -> None:
        first = self.a_subscription(self.MISSION_ID)
        second = self.a_subscription(self.OTHER_MISSION_ID)
        session = LiveSession(stand_in_socket, source, codec, config)
        task = asyncio.create_task(self.drain(session, []))
        stand_in_socket.feed(codec.encode_subscription(first))
        stand_in_socket.feed(codec.encode_subscription(second))
        await self.wait_for_watchers(hub, first.topic, 1)
        await self.wait_for_watchers(hub, second.topic, 1)
        stand_in_socket.disconnect()
        await asyncio.wait_for(task, timeout=2.0)
        assert hub.watchers(first.topic) == 0
        assert hub.watchers(second.topic) == 0
