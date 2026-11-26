from __future__ import annotations

# Standard library imports
from datetime import UTC, datetime
from typing import ClassVar, Dict, Optional
from uuid import UUID

# Third-party imports
import pytest
from nats.aio.client import Client
from nats.js.errors import NotFoundError
from pydantic import JsonValue

# First-party imports
from swarm_models.events.actor import Actor
from swarm_models.events.enums import ActorKind
from swarm_models.events.event import Event
from swarm_nats.clients.event_publisher import EventPublisher
from swarm_nats.clients.jetstream_admin import JetStreamAdmin
from swarm_nats.models.bus.exceptions import SENatsPublishError
from swarm_nats.models.bus.nats_headers import NatsHeaders
from swarm_nats.models.streams.stream_spec import StreamSpec
from swarm_nats.models.subjects.operator_subjects import OperatorSubjects


class TestEventPublisher:
    STREAM_NAME: ClassVar[str] = "OPS"
    STREAM_SUBJECTS: ClassVar[str] = "op.>"
    OTHER_STREAM_SUBJECT: ClassVar[str] = "other.>"
    EVENT_ID: ClassVar[UUID] = UUID("01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e5f")
    OPERATOR_ID: ClassVar[UUID] = UUID("01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e60")
    MISSION_ID: ClassVar[UUID] = UUID("01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e61")
    PERSON_ID: ClassVar[UUID] = UUID("01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e62")
    OCCURRED_AT: ClassVar[datetime] = datetime(2026, 11, 19, 10, 30, 15, 123456, tzinfo=UTC)
    PAYLOAD: ClassVar[Dict[str, JsonValue]] = {"name": "Survey"}
    MISSION_TYPE: ClassVar[str] = "mission.planned"
    FLEET_TYPE: ClassVar[str] = "drone.position"
    SINGLE_REPLICA: ClassVar[int] = 1
    ONE_MESSAGE: ClassVar[int] = 1

    def build(self, event_type: str, mission_id: Optional[UUID]) -> Event:
        return Event(
            id=self.EVENT_ID,
            type=event_type,
            operator_id=self.OPERATOR_ID,
            mission_id=mission_id,
            occurred_at=self.OCCURRED_AT,
            actor=Actor(kind=ActorKind.PERSON, person_id=self.PERSON_ID),
            payload=self.PAYLOAD,
        )

    async def create_stream(self, nats_client: Client, name: str, subject: str) -> None:
        try:
            await nats_client.jetstream().delete_stream(name)
        except NotFoundError:
            pass
        await JetStreamAdmin(nats_client).ensure_stream(
            StreamSpec(name=name, subjects=[subject], replicas=self.SINGLE_REPLICA)
        )

    async def test_a_mission_event_lands_on_its_mission_subject(self, nats_client: Client) -> None:
        await self.create_stream(nats_client, self.STREAM_NAME, self.STREAM_SUBJECTS)
        event = self.build(self.MISSION_TYPE, self.MISSION_ID)
        sequence = await EventPublisher(nats_client).publish(event)
        message = await nats_client.jetstream().get_msg(self.STREAM_NAME, seq=sequence)
        assert message.subject == OperatorSubjects(operator_id=self.OPERATOR_ID).for_event(event)
        assert message.subject == f"op.{self.OPERATOR_ID}.mission.{self.MISSION_ID}.{self.MISSION_TYPE}"
        assert message.data is not None
        assert Event.model_validate_json(message.data) == event
        assert message.headers is not None
        assert message.headers[NatsHeaders.MSG_ID] == str(event.id)

    async def test_a_fleet_event_lands_on_its_fleet_subject(self, nats_client: Client) -> None:
        await self.create_stream(nats_client, self.STREAM_NAME, self.STREAM_SUBJECTS)
        event = self.build(self.FLEET_TYPE, None)
        sequence = await EventPublisher(nats_client).publish(event)
        message = await nats_client.jetstream().get_msg(self.STREAM_NAME, seq=sequence)
        assert message.subject == f"op.{self.OPERATOR_ID}.fleet.{self.FLEET_TYPE}"

    async def test_the_same_event_published_twice_is_stored_once(self, nats_client: Client) -> None:
        await self.create_stream(nats_client, self.STREAM_NAME, self.STREAM_SUBJECTS)
        event = self.build(self.MISSION_TYPE, self.MISSION_ID)
        publisher = EventPublisher(nats_client)
        first = await publisher.publish(event)
        second = await publisher.publish(event)
        assert first == second
        info = await nats_client.jetstream().stream_info(self.STREAM_NAME)
        assert info.state.messages == self.ONE_MESSAGE

    async def test_an_event_that_no_stream_captures_is_refused(self, nats_client: Client) -> None:
        await self.create_stream(nats_client, self.STREAM_NAME, self.OTHER_STREAM_SUBJECT)
        event = self.build(self.MISSION_TYPE, self.MISSION_ID)
        with pytest.raises(SENatsPublishError):
            await EventPublisher(nats_client).publish(event)
