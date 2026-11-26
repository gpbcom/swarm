from __future__ import annotations

# Standard library imports
import asyncio
from typing import ClassVar, List
from uuid import UUID

# Third-party imports
import pytest
from nats.aio.client import Client

# First-party imports
from gateway.models.live.exceptions import SELiveFeedNotReadyError
from gateway.models.live.live_config import LiveConfig
from gateway.service.live.live_feed import LiveFeed
from swarm_lifecycle.models.enums import RunnableStatus
from swarm_models.enums import LiveOperation, LiveTopicKind
from swarm_models.live.live_subscription import LiveSubscription
from swarm_models.subjects.operator_subjects import OperatorSubjects
from swarm_nats.clients.nats_connector import NatsConnector
from swarm_nats.models.config.nats_client_config import NatsClientConfig

from swarm_live.models.config.live_session_config import LiveSessionConfig  # isort: skip
from swarm_live.service.live_hub import LiveHub  # isort: skip


class TestLiveFeed:
    OPERATOR_ID: ClassVar[UUID] = UUID("01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e60")
    MISSION_ID: ClassVar[UUID] = UUID("01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e61")
    PAYLOAD: ClassVar[bytes] = b"squad-frame"
    INTERVAL_S: ClassVar[float] = 0.05
    WAIT_S: ClassVar[float] = 5.0
    LIVE_STATUSES: ClassVar[List[RunnableStatus]] = [RunnableStatus.INITIALISING, RunnableStatus.RUNNING]

    def feed(self, nats_url: str) -> LiveFeed:
        config = LiveConfig(
            status_interval_s=self.INTERVAL_S,
            nats=NatsClientConfig(servers=[nats_url]),
            session=LiveSessionConfig(),
        )
        return LiveFeed(config, NatsConnector(config.nats), LiveHub())

    def test_a_feed_that_is_not_initialised_refuses_a_source(self, nats_url: str) -> None:
        with pytest.raises(SELiveFeedNotReadyError):
            self.feed(nats_url).source_for(self.OPERATOR_ID)

    async def test_execute_yields_statuses_and_serves_frames_while_running(
        self, nats_url: str, nats_client: Client
    ) -> None:
        feed = self.feed(nats_url)
        subscription = LiveSubscription(
            op=LiveOperation.SUBSCRIBE, topic=LiveSubscription.topic_of(self.MISSION_ID, LiveTopicKind.SQUAD)
        )
        subject = OperatorSubjects(operator_id=self.OPERATOR_ID).mission(self.MISSION_ID, LiveTopicKind.SQUAD)
        statuses: List[RunnableStatus] = []
        received: List[bytes] = []
        execution = feed.execute()
        try:
            async for status in execution:
                statuses.append(status)
                if status is RunnableStatus.RUNNING:
                    mailbox = await feed.source_for(self.OPERATOR_ID).join(subscription)
                    await nats_client.publish(subject, self.PAYLOAD)
                    received.append(await asyncio.wait_for(mailbox.take(), self.WAIT_S))
                    break
        finally:
            await execution.aclose()
        assert statuses
        assert all(isinstance(status, RunnableStatus) for status in statuses)
        assert set(statuses) <= set(self.LIVE_STATUSES)
        assert received == [self.PAYLOAD]

    async def test_a_feed_that_was_closed_refuses_a_source(self, nats_url: str) -> None:
        feed = self.feed(nats_url)
        execution = feed.execute()
        try:
            async for status in execution:
                if status is RunnableStatus.RUNNING:
                    break
        finally:
            await execution.aclose()
        with pytest.raises(SELiveFeedNotReadyError):
            feed.source_for(self.OPERATOR_ID)
