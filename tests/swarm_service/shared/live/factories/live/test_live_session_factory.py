from __future__ import annotations

# Standard library imports
from typing import ClassVar, Dict

# Third-party imports
import pytest
from starlette.types import Message
from starlette.websockets import WebSocket

# First-party imports
from swarm_lifecycle.factories.async_runnable_factory import AsyncRunnableFactory
from swarm_models.live.session.live_session_config import LiveSessionConfig
from swarm_service.shared.live.factories.live.live_session_factory import LiveSessionFactory
from swarm_service.shared.live.factories.live_runnable_factory import LiveRunnableFactory
from swarm_service.shared.live.hub.live_hub import LiveHub
from swarm_service.shared.live.live_codec import LiveCodec
from swarm_service.shared.live.live_session import LiveSession
from swarm_service.shared.live.sources.hub_live_source import HubLiveSource


class TestLiveSessionFactory:
    SCOPE: ClassVar[Dict[str, str]] = {"type": "websocket"}

    async def receive(self) -> Message:
        return {"type": "websocket.disconnect", "code": 1000}

    async def send(self, message: Message) -> None:
        return None

    def a_factory(self) -> LiveSessionFactory:
        socket = WebSocket(dict(self.SCOPE), self.receive, self.send)
        source = HubLiveSource(LiveHub())
        return LiveSessionFactory(socket, source, LiveCodec(), LiveSessionConfig(status_interval_s=0.05))

    def test_the_abstract_factory_cannot_be_instantiated(self) -> None:
        with pytest.raises(TypeError):
            LiveRunnableFactory()

    def test_the_factory_is_an_async_runnable_factory(self) -> None:
        assert issubclass(LiveRunnableFactory, AsyncRunnableFactory)
        assert issubclass(LiveSessionFactory, LiveRunnableFactory)

    def test_create_returns_a_live_session(self) -> None:
        assert isinstance(self.a_factory().create(), LiveSession)

    def test_create_returns_a_new_session_each_time(self) -> None:
        factory = self.a_factory()
        assert factory.create() is not factory.create()
