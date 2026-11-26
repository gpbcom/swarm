from __future__ import annotations

# Standard library imports
import asyncio
from typing import ClassVar
from uuid import UUID

# Third-party imports
import pytest
from nats.aio.client import Client

# First-party imports
from gateway.clients.nats.mission_feed_client import MissionFeedClient
from gateway.service.live.live_fan_out import LiveFanOut
from gateway.service.live.operator_live_source import OperatorLiveSource
from swarm_models.enums import LiveOperation, LiveTopicKind
from swarm_models.live.live_subscription import LiveSubscription
from swarm_nats.models.subjects.operator_subjects import OperatorSubjects

from swarm_live.service.live_hub import LiveHub  # isort: skip
from swarm_live.service.live_source import LiveSource  # isort: skip


class TestOperatorLiveSource:
    OPERATOR_A: ClassVar[UUID] = UUID("01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e60")
    OPERATOR_B: ClassVar[UUID] = UUID("01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e70")
    MISSION_ID: ClassVar[UUID] = UUID("01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e61")
    PAYLOAD: ClassVar[bytes] = b"squad-frame"
    WAIT_S: ClassVar[float] = 5.0
    QUIET_S: ClassVar[float] = 0.3

    @pytest.fixture
    def fan_out(self, nats_client: Client) -> LiveFanOut:
        return LiveFanOut(LiveHub(), MissionFeedClient(nats_client))

    def subscription(self) -> LiveSubscription:
        return LiveSubscription(
            op=LiveOperation.SUBSCRIBE, topic=LiveSubscription.topic_of(self.MISSION_ID, LiveTopicKind.SQUAD)
        )

    def subject(self, operator_id: UUID) -> str:
        return OperatorSubjects(operator_id=operator_id).mission(self.MISSION_ID, LiveTopicKind.SQUAD)

    def test_the_source_is_a_live_source(self, fan_out: LiveFanOut) -> None:
        assert isinstance(OperatorLiveSource(self.OPERATOR_A, fan_out), LiveSource)
        assert isinstance(fan_out.source_for(self.OPERATOR_A), LiveSource)

    async def test_a_source_joins_under_its_own_operator(self, fan_out: LiveFanOut, nats_client: Client) -> None:
        source = OperatorLiveSource(self.OPERATOR_A, fan_out)
        mailbox = await source.join(self.subscription())
        assert fan_out.subjects() == [self.subject(self.OPERATOR_A)]
        await nats_client.publish(self.subject(self.OPERATOR_A), self.PAYLOAD)
        assert await asyncio.wait_for(mailbox.take(), self.WAIT_S) == self.PAYLOAD

    async def test_a_source_never_sees_the_frames_of_another_operator(
        self, fan_out: LiveFanOut, nats_client: Client
    ) -> None:
        mailbox = await fan_out.source_for(self.OPERATOR_A).join(self.subscription())
        await nats_client.publish(self.subject(self.OPERATOR_B), self.PAYLOAD)
        await nats_client.flush()
        await asyncio.sleep(self.QUIET_S)
        assert not mailbox.pending()

    async def test_leaving_through_the_source_ends_the_subscription(self, fan_out: LiveFanOut) -> None:
        source = OperatorLiveSource(self.OPERATOR_A, fan_out)
        mailbox = await source.join(self.subscription())
        await source.leave(self.subscription(), mailbox)
        assert fan_out.subjects() == []
