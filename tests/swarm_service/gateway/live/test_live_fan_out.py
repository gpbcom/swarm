from __future__ import annotations

# Standard library imports
import asyncio
from typing import ClassVar, List
from uuid import UUID

# Third-party imports
import pytest
from nats.aio.client import Client

# First-party imports
from gateway.clients.nats.mission_feed_client import MissionFeedClient
from gateway.service.live.live_fan_out import LiveFanOut
from swarm_models.enums import LiveOperation, LiveTopicKind
from swarm_models.live.live_subscription import LiveSubscription
from swarm_models.subjects.operator_subjects import OperatorSubjects

from swarm_live.service.live_hub import LiveHub  # isort: skip


class TestLiveFanOut:
    OPERATOR_A: ClassVar[UUID] = UUID("01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e60")
    OPERATOR_B: ClassVar[UUID] = UUID("01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e70")
    MISSION_ID: ClassVar[UUID] = UUID("01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e61")
    PAYLOAD: ClassVar[bytes] = b"squad-frame"
    FRAMES: ClassVar[int] = 20
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

    async def test_two_clients_of_one_mission_make_one_subscription(
        self, fan_out: LiveFanOut, nats_client: Client
    ) -> None:
        first = await fan_out.join(self.OPERATOR_A, self.subscription())
        second = await fan_out.join(self.OPERATOR_A, self.subscription())
        assert fan_out.subjects() == [self.subject(self.OPERATOR_A)]
        await nats_client.publish(self.subject(self.OPERATOR_A), self.PAYLOAD)
        assert await asyncio.wait_for(first.take(), self.WAIT_S) == self.PAYLOAD
        assert await asyncio.wait_for(second.take(), self.WAIT_S) == self.PAYLOAD

    async def test_the_subscription_stays_while_one_client_remains_and_goes_with_the_last(
        self, fan_out: LiveFanOut
    ) -> None:
        first = await fan_out.join(self.OPERATOR_A, self.subscription())
        second = await fan_out.join(self.OPERATOR_A, self.subscription())
        await fan_out.leave(self.OPERATOR_A, self.subscription(), first)
        assert fan_out.subjects() == [self.subject(self.OPERATOR_A)]
        await fan_out.leave(self.OPERATOR_A, self.subscription(), second)
        assert fan_out.subjects() == []

    async def test_a_client_of_one_operator_gets_nothing_of_another_operator(
        self, fan_out: LiveFanOut, nats_client: Client
    ) -> None:
        mailbox = await fan_out.join(self.OPERATOR_A, self.subscription())
        await nats_client.publish(self.subject(self.OPERATOR_B), self.PAYLOAD)
        await nats_client.flush()
        await asyncio.sleep(self.QUIET_S)
        assert not mailbox.pending()

    async def test_the_two_operators_of_one_mission_id_make_two_subscriptions(self, fan_out: LiveFanOut) -> None:
        await fan_out.join(self.OPERATOR_A, self.subscription())
        await fan_out.join(self.OPERATOR_B, self.subscription())
        assert sorted(fan_out.subjects()) == sorted([self.subject(self.OPERATOR_A), self.subject(self.OPERATOR_B)])

    async def test_a_client_that_does_not_take_its_mailbox_holds_only_the_last_frame(self, fan_out: LiveFanOut) -> None:
        mailbox = await fan_out.join(self.OPERATOR_A, self.subscription())
        frames: List[bytes] = [str(index).encode() for index in range(self.FRAMES)]
        for frame in frames:
            fan_out.deliver(self.subject(self.OPERATOR_A), frame)
        assert await asyncio.wait_for(mailbox.take(), self.WAIT_S) == frames[-1]
        assert mailbox.skipped == self.FRAMES - 1
        assert not mailbox.pending()

    async def test_a_frame_for_a_subject_nobody_watches_is_dropped(self, fan_out: LiveFanOut) -> None:
        mailbox = await fan_out.join(self.OPERATOR_A, self.subscription())
        fan_out.deliver(self.subject(self.OPERATOR_B), self.PAYLOAD)
        assert not mailbox.pending()
