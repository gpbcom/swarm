from __future__ import annotations

# Standard library imports
from typing import ClassVar
from uuid import UUID

# First-party imports
from swarm_live.service.hub_live_source import HubLiveSource  # isort: skip
from swarm_live.service.live_hub import LiveHub  # isort: skip
from swarm_live.service.live_source import LiveSource  # isort: skip
from swarm_models.enums import LiveOperation, LiveTopicKind
from swarm_models.live.live_subscription import LiveSubscription


class TestHubLiveSource:
    MISSION_ID: ClassVar[UUID] = UUID("01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e5f")

    def a_subscription(self) -> LiveSubscription:
        topic = LiveSubscription.topic_of(self.MISSION_ID, LiveTopicKind.SQUAD)
        return LiveSubscription(op=LiveOperation.SUBSCRIBE, topic=topic)

    def test_the_source_is_a_live_source(self) -> None:
        assert isinstance(HubLiveSource(LiveHub()), LiveSource)

    async def test_join_subscribes_the_hub_under_the_topic(self) -> None:
        hub = LiveHub()
        subscription = self.a_subscription()
        mailbox = await HubLiveSource(hub).join(subscription)
        assert hub.watchers(subscription.topic) == 1
        hub.publish(subscription.topic, b"frame")
        assert await mailbox.take() == b"frame"

    async def test_leave_unsubscribes_the_mailbox(self) -> None:
        hub = LiveHub()
        subscription = self.a_subscription()
        source = HubLiveSource(hub)
        mailbox = await source.join(subscription)
        await source.leave(subscription, mailbox)
        assert hub.watchers(subscription.topic) == 0
        assert hub.publish(subscription.topic, b"frame") == 0

    async def test_two_joins_get_their_own_mailboxes(self) -> None:
        hub = LiveHub()
        subscription = self.a_subscription()
        source = HubLiveSource(hub)
        first = await source.join(subscription)
        second = await source.join(subscription)
        assert first is not second
        assert hub.watchers(subscription.topic) == 2
