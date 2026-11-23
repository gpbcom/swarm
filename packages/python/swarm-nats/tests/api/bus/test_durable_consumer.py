from __future__ import annotations

# Standard library imports
import asyncio
from datetime import UTC, datetime
from typing import ClassVar, Dict, List, Set
from uuid import UUID

# Third-party imports
from nats.aio.client import Client
from nats.js.api import StreamConfig

# First-party imports
from swarm_lifecycle.models.enums import RunnableStatus
from swarm_models.models.events.actor import Actor
from swarm_models.models.events.enums import ActorKind
from swarm_models.models.events.event import Event
from swarm_nats.api.bus.durable_consumer import DurableConsumer
from swarm_nats.models.config.durable_consumer_config import DurableConsumerConfig


class TestDurableConsumer:
    STREAM: ClassVar[str] = "OPS"
    SUBJECTS: ClassVar[List[str]] = ["op.>"]
    DURABLE_NAME: ClassVar[str] = "projector"
    MSG_ID_HEADER: ClassVar[str] = "Nats-Msg-Id"
    INDEX_KEY: ClassVar[str] = "index"
    OPERATOR_ID: ClassVar[str] = "01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e60"
    PERSON_ID: ClassVar[str] = "01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e62"
    EVENT_ID_TEMPLATE: ClassVar[str] = "01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e{index:02x}"
    EVENT_TYPE: ClassVar[str] = "mission.planned"
    OCCURRED_AT: ClassVar[datetime] = datetime(2026, 11, 19, 10, 30, 15, tzinfo=UTC)
    NOT_AN_EVENT: ClassVar[bytes] = b"this is not an event"
    NOT_AN_EVENT_ID: ClassVar[str] = "not-an-event-1"
    WAIT_LIMIT_S: ClassVar[float] = 10.0
    POLL_S: ClassVar[float] = 0.05
    ACK_WAIT_S: ClassVar[float] = 1.0

    def setup_method(self) -> None:
        self.handled: List[Event] = []
        self.attempts: List[UUID] = []
        self.failing: Set[UUID] = set()
        self.statuses: List[RunnableStatus] = []

    def event(self, index: int) -> Event:
        return Event(
            id=UUID(self.EVENT_ID_TEMPLATE.format(index=index)),
            type=self.EVENT_TYPE,
            operator_id=UUID(self.OPERATOR_ID),
            occurred_at=self.OCCURRED_AT,
            actor=Actor(kind=ActorKind.PERSON, person_id=UUID(self.PERSON_ID)),
            payload={self.INDEX_KEY: index},
        )

    def subject(self) -> str:
        return f"op.{self.OPERATOR_ID}.{self.EVENT_TYPE}"

    def config(self, ack_wait_s: float) -> DurableConsumerConfig:
        return DurableConsumerConfig(
            stream=self.STREAM,
            durable_name=self.DURABLE_NAME,
            batch_size=10,
            fetch_timeout_s=0.2,
            ack_wait_s=ack_wait_s,
            status_interval_s=0.1,
        )

    def consumer(self, client: Client, ack_wait_s: float = 30.0) -> DurableConsumer[Event]:
        return DurableConsumer(client, self.config(ack_wait_s), Event, self.handle)

    async def handle(self, event: Event) -> None:
        self.attempts.append(event.id)
        if event.id in self.failing:
            self.failing.discard(event.id)
            raise RuntimeError("The handler fails on the first delivery.")
        self.handled.append(event)

    async def read(self, consumer: DurableConsumer[Event]) -> None:
        async for status in consumer.execute():
            self.statuses.append(status)

    async def create_stream(self, client: Client) -> None:
        await client.jetstream().add_stream(StreamConfig(name=self.STREAM, subjects=self.SUBJECTS, num_replicas=1))

    async def publish(self, client: Client, event: Event) -> None:
        headers: Dict[str, str] = {self.MSG_ID_HEADER: str(event.id)}
        await client.jetstream().publish(self.subject(), event.model_dump_json().encode(), headers=headers)

    async def publish_garbage(self, client: Client) -> None:
        headers: Dict[str, str] = {self.MSG_ID_HEADER: self.NOT_AN_EVENT_ID}
        await client.jetstream().publish(self.subject(), self.NOT_AN_EVENT, headers=headers)

    async def wait_handled(self, count: int) -> None:
        async with asyncio.timeout(self.WAIT_LIMIT_S):
            while len(self.handled) < count:
                await asyncio.sleep(self.POLL_S)

    async def wait_acknowledged(self, client: Client) -> None:
        async with asyncio.timeout(self.WAIT_LIMIT_S):
            while (await client.jetstream().consumer_info(self.STREAM, self.DURABLE_NAME)).num_ack_pending:
                await asyncio.sleep(self.POLL_S)

    async def wait_running(self) -> None:
        async with asyncio.timeout(self.WAIT_LIMIT_S):
            while RunnableStatus.RUNNING not in self.statuses:
                await asyncio.sleep(self.POLL_S)

    async def cancel(self, task: asyncio.Task[None]) -> None:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            return

    async def test_three_events_are_handled_in_publication_order_and_acknowledged(self, nats_client: Client) -> None:
        await self.create_stream(nats_client)
        events = [self.event(index) for index in range(1, 4)]
        for event in events:
            await self.publish(nats_client, event)
        task = asyncio.create_task(self.read(self.consumer(nats_client)))
        await self.wait_handled(len(events))
        await self.wait_acknowledged(nats_client)
        await self.cancel(task)
        info = await nats_client.jetstream().consumer_info(self.STREAM, self.DURABLE_NAME)
        assert [event.id for event in self.handled] == [event.id for event in events]
        assert info.num_ack_pending == 0

    async def test_a_new_consumer_with_the_same_durable_name_receives_only_the_new_events(
        self, nats_client: Client
    ) -> None:
        await self.create_stream(nats_client)
        for index in (1, 2):
            await self.publish(nats_client, self.event(index))
        first = asyncio.create_task(self.read(self.consumer(nats_client)))
        await self.wait_handled(2)
        await self.wait_acknowledged(nats_client)
        await self.cancel(first)
        for index in (3, 4):
            await self.publish(nats_client, self.event(index))
        second = asyncio.create_task(self.read(self.consumer(nats_client)))
        await self.wait_handled(4)
        await self.cancel(second)
        assert [event.id for event in self.handled] == [self.event(index).id for index in (1, 2, 3, 4)]

    async def test_a_handler_that_raises_receives_the_event_again(self, nats_client: Client) -> None:
        await self.create_stream(nats_client)
        event = self.event(1)
        self.failing.add(event.id)
        await self.publish(nats_client, event)
        task = asyncio.create_task(self.read(self.consumer(nats_client, self.ACK_WAIT_S)))
        await self.wait_handled(1)
        await self.wait_acknowledged(nats_client)
        await self.cancel(task)
        assert self.attempts == [event.id, event.id]
        assert [handled.id for handled in self.handled] == [event.id]

    async def test_a_message_that_is_not_an_event_is_never_handled_nor_redelivered(self, nats_client: Client) -> None:
        await self.create_stream(nats_client)
        await self.publish_garbage(nats_client)
        event = self.event(1)
        await self.publish(nats_client, event)
        task = asyncio.create_task(self.read(self.consumer(nats_client, self.ACK_WAIT_S)))
        await self.wait_handled(1)
        await self.wait_acknowledged(nats_client)
        await asyncio.sleep(self.ACK_WAIT_S * 2)
        await self.cancel(task)
        info = await nats_client.jetstream().consumer_info(self.STREAM, self.DURABLE_NAME)
        assert self.attempts == [event.id]
        assert info.num_redelivered == 0
        assert info.num_ack_pending == 0

    async def test_execute_yields_running_while_consuming(self, nats_client: Client) -> None:
        await self.create_stream(nats_client)
        await self.publish(nats_client, self.event(1))
        task = asyncio.create_task(self.read(self.consumer(nats_client)))
        await self.wait_handled(1)
        await self.wait_running()
        await self.cancel(task)
        assert RunnableStatus.RUNNING in self.statuses
