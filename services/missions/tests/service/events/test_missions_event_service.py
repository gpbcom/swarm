from __future__ import annotations

from datetime import UTC, datetime
from typing import AsyncIterator, ClassVar, Dict
from uuid import UUID

import pytest
from pydantic import JsonValue

from missions.models.config.missions_config import MissionsConfig
from missions.service.events.event_service import EventService
from missions.service.factories.event_service_factory import EventServiceFactory
from missions.service.factories.schema_service_factory import SchemaServiceFactory
from swarm_models.models.events.actor import Actor
from swarm_models.models.events.enums import ActorKind
from swarm_models.models.events.event import Event


class TestMissionsEventService:
    OPERATOR_A: ClassVar[UUID] = UUID("01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e60")
    OPERATOR_B: ClassVar[UUID] = UUID("01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e61")
    PERSON_ID: ClassVar[UUID] = UUID("01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e62")
    EVENT_A1: ClassVar[UUID] = UUID("01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e71")
    EVENT_A2: ClassVar[UUID] = UUID("01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e72")
    EVENT_B1: ClassVar[UUID] = UUID("01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e73")
    EVENT_B2: ClassVar[UUID] = UUID("01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e74")
    EVENT_TYPE: ClassVar[str] = "mission.planned"
    OCCURRED_AT: ClassVar[datetime] = datetime(2026, 11, 19, 10, 30, 15, 123456, tzinfo=UTC)
    PAYLOAD: ClassVar[Dict[str, JsonValue]] = {"name": "Survey"}

    def an_event(self, event_id: UUID, operator_id: UUID) -> Event:
        return Event(
            id=event_id,
            type=self.EVENT_TYPE,
            operator_id=operator_id,
            occurred_at=self.OCCURRED_AT,
            actor=Actor(kind=ActorKind.PERSON, person_id=self.PERSON_ID),
            payload=dict(self.PAYLOAD),
        )

    @pytest.fixture
    async def service(self, postgres_dsn: str, monkeypatch: pytest.MonkeyPatch) -> AsyncIterator[EventService]:
        monkeypatch.setenv(MissionsConfig.DSN_KEY, postgres_dsn)
        await SchemaServiceFactory(MissionsConfig()).create().upgrade()
        events = EventServiceFactory(MissionsConfig()).create()
        await events.open()
        try:
            await events.record(self.an_event(self.EVENT_A1, self.OPERATOR_A))
            await events.record(self.an_event(self.EVENT_A2, self.OPERATOR_A))
            await events.record(self.an_event(self.EVENT_B1, self.OPERATOR_B))
            yield events
        finally:
            await events.close()

    async def test_pending_returns_only_the_events_of_operator_a(self, service: EventService) -> None:
        pending = await service.pending(self.OPERATOR_A)
        assert [event.id for event in pending] == [self.EVENT_A1, self.EVENT_A2]
        assert {event.operator_id for event in pending} == {self.OPERATOR_A}

    async def test_pending_returns_only_the_events_of_operator_b(self, service: EventService) -> None:
        pending = await service.pending(self.OPERATOR_B)
        assert [event.id for event in pending] == [self.EVENT_B1]
        assert {event.operator_id for event in pending} == {self.OPERATOR_B}

    async def test_a_query_without_an_operator_returns_nothing(self, service: EventService) -> None:
        assert await service.pending(None) == []

    async def test_pending_honours_its_limit(self, service: EventService) -> None:
        pending = await service.pending(self.OPERATOR_A, limit=1)
        assert [event.id for event in pending] == [self.EVENT_A1]

    async def test_record_returns_the_event(self, service: EventService) -> None:
        event = self.an_event(self.EVENT_B2, self.OPERATOR_B)
        assert await service.record(event) == event

    async def test_close_is_safe_twice(self, service: EventService) -> None:
        await service.close()
        await service.close()
