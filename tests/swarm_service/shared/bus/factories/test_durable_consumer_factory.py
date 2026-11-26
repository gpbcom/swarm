from __future__ import annotations

# Standard library imports
from typing import ClassVar

# Third-party imports
from nats.aio.client import Client

# First-party imports
from swarm_lifecycle.models.enums import RunnableStatus
from swarm_models.events.event import Event
from swarm_nats.api.bus.durable_consumer import DurableConsumer
from swarm_nats.api.factories.bus.durable_consumer_factory import DurableConsumerFactory
from swarm_nats.api.factories.bus_runnable_factory import BusRunnableFactory
from swarm_nats.models.config.durable_consumer_config import DurableConsumerConfig


class TestDurableConsumerFactory:
    STREAM: ClassVar[str] = "OPS"
    DURABLE_NAME: ClassVar[str] = "projector"
    STATUS_INTERVAL_S: ClassVar[float] = 0.25

    async def handle(self, event: Event) -> None:
        return None

    def factory(self) -> DurableConsumerFactory[Event]:
        config = DurableConsumerConfig(
            stream=self.STREAM, durable_name=self.DURABLE_NAME, status_interval_s=self.STATUS_INTERVAL_S
        )
        return DurableConsumerFactory(Client(), config, Event, self.handle)

    def test_the_factory_is_a_bus_runnable_factory(self) -> None:
        assert isinstance(self.factory(), BusRunnableFactory)

    def test_create_returns_a_consumer_that_is_not_started(self) -> None:
        consumer = self.factory().create()
        assert isinstance(consumer, DurableConsumer)
        assert consumer.status == RunnableStatus.NOT_STARTED
        assert consumer.status_interval_s == self.STATUS_INTERVAL_S

    def test_two_calls_return_distinct_instances(self) -> None:
        factory = self.factory()
        assert factory.create() is not factory.create()
