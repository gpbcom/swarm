from __future__ import annotations

# Standard library imports
import asyncio
from typing import ClassVar, List, Tuple

# Third-party imports
import pytest
from nats.aio.client import Client

# First-party imports
from gateway.clients.nats.mission_feed_client import MissionFeedClient
from gateway.models.live.exceptions import SEMissionFeedError


class TestMissionFeedClient:
    SUBJECT: ClassVar[str] = (
        "op.01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e60.mission.01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e61.squad"
    )
    OTHER_SUBJECT: ClassVar[str] = (
        "op.01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e60.mission.01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e62.squad"
    )
    PAYLOAD: ClassVar[bytes] = b"frame-one"
    WAIT_S: ClassVar[float] = 5.0
    QUIET_S: ClassVar[float] = 0.3

    received: List[Tuple[str, bytes]]
    arrived: asyncio.Event

    def on_frame(self, subject: str, data: bytes) -> None:
        self.received.append((subject, data))
        self.arrived.set()

    async def test_a_published_frame_reaches_the_handler_with_its_subject(self, nats_client: Client) -> None:
        self.received = []
        self.arrived = asyncio.Event()
        feed = MissionFeedClient(nats_client)
        await feed.subscribe(self.SUBJECT, self.on_frame)
        await nats_client.publish(self.SUBJECT, self.PAYLOAD)
        await asyncio.wait_for(self.arrived.wait(), self.WAIT_S)
        assert self.received == [(self.SUBJECT, self.PAYLOAD)]

    async def test_subjects_lists_the_subscribed_subjects(self, nats_client: Client) -> None:
        feed = MissionFeedClient(nats_client)
        assert feed.subjects() == []
        await feed.subscribe(self.SUBJECT, lambda subject, data: None)
        await feed.subscribe(self.OTHER_SUBJECT, lambda subject, data: None)
        assert sorted(feed.subjects()) == sorted([self.SUBJECT, self.OTHER_SUBJECT])

    async def test_an_unsubscribed_subject_delivers_nothing_more(self, nats_client: Client) -> None:
        received: List[bytes] = []
        feed = MissionFeedClient(nats_client)
        await feed.subscribe(self.SUBJECT, lambda subject, data: received.append(data))
        await feed.unsubscribe(self.SUBJECT)
        await nats_client.publish(self.SUBJECT, self.PAYLOAD)
        await nats_client.flush()
        await asyncio.sleep(self.QUIET_S)
        assert received == []
        assert feed.subjects() == []

    async def test_a_handler_gets_only_its_own_subject(self, nats_client: Client) -> None:
        received: List[bytes] = []
        feed = MissionFeedClient(nats_client)
        await feed.subscribe(self.SUBJECT, lambda subject, data: received.append(data))
        await nats_client.publish(self.OTHER_SUBJECT, self.PAYLOAD)
        await nats_client.flush()
        await asyncio.sleep(self.QUIET_S)
        assert received == []

    async def test_a_closed_connection_raises_the_feed_error(self, nats_client: Client) -> None:
        feed = MissionFeedClient(nats_client)
        await nats_client.close()
        with pytest.raises(SEMissionFeedError):
            await feed.subscribe(self.SUBJECT, lambda subject, data: None)
