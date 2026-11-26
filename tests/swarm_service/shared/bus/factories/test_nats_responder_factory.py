from __future__ import annotations

# Third-party imports
import pytest
from nats.aio.client import Client

# First-party imports
from swarm_lifecycle.models.enums import RunnableStatus
from swarm_models.config.nats.nats_responder_config import NatsResponderConfig
from swarm_models.streams.stream_source import StreamSource
from swarm_service.shared.bus.factories.bus_runnable_factory import BusRunnableFactory
from swarm_service.shared.bus.factories.nats_responder_factory import NatsResponderFactory
from swarm_service.shared.bus.nats_responder import NatsResponder


class TestNatsResponderFactory:
    @pytest.fixture
    def config(self) -> NatsResponderConfig:
        return NatsResponderConfig(subject="svc.echo", queue_group="echo_workers", replicas=1, status_interval_s=0.25)

    @pytest.fixture
    def factory(self, config: NatsResponderConfig) -> NatsResponderFactory[StreamSource, StreamSource]:
        return NatsResponderFactory(Client(), config, StreamSource, self.handle)

    async def handle(self, request: StreamSource) -> StreamSource:
        return request

    def test_create_returns_a_responder_not_started_with_the_configured_interval(
        self, factory: NatsResponderFactory[StreamSource, StreamSource], config: NatsResponderConfig
    ) -> None:
        responder = factory.create()
        assert isinstance(responder, NatsResponder)
        assert responder.status == RunnableStatus.NOT_STARTED
        assert responder.status_interval_s == config.status_interval_s

    def test_two_calls_return_two_distinct_instances(
        self, factory: NatsResponderFactory[StreamSource, StreamSource]
    ) -> None:
        assert factory.create() is not factory.create()

    def test_the_factory_is_a_bus_runnable_factory(
        self, factory: NatsResponderFactory[StreamSource, StreamSource]
    ) -> None:
        assert isinstance(factory, BusRunnableFactory)
