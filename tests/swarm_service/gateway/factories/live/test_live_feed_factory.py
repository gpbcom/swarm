from __future__ import annotations

# First-party imports
from gateway.models.live.live_config import LiveConfig
from gateway.service.factories.live.live_feed_factory import LiveFeedFactory
from gateway.service.factories.live_service_factory import LiveServiceFactory
from gateway.service.live.live_feed import LiveFeed
from swarm_lifecycle.factories.async_runnable_factory import AsyncRunnableFactory


class TestLiveFeedFactory:
    def test_the_factory_is_a_live_service_factory(self) -> None:
        assert issubclass(LiveFeedFactory, LiveServiceFactory)
        assert issubclass(LiveServiceFactory, AsyncRunnableFactory)

    def test_create_builds_a_live_feed(self) -> None:
        feed = LiveFeedFactory(LiveConfig()).create()
        assert isinstance(feed, LiveFeed)

    def test_each_create_builds_a_new_live_feed(self) -> None:
        factory = LiveFeedFactory(LiveConfig())
        assert factory.create() is not factory.create()
