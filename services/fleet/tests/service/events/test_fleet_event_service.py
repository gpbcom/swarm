from __future__ import annotations

# Standard library imports
from datetime import UTC, datetime
from typing import AsyncIterator, ClassVar, Dict, List, Optional
from uuid import UUID

# Third-party imports
import pytest
from pydantic import JsonValue

# First-party imports
from fleet.models.config.fleet_config import FleetConfig
from fleet.service.events.event_service import EventService
from fleet.service.factories.event_service_factory import EventServiceFactory
from fleet.service.factories.schema_service_factory import SchemaServiceFactory
from swarm_models.models.events.actor import Actor
from swarm_models.models.events.enums import ActorKind
from swarm_models.models.events.event import Event


class TestFleetEventService:
    OPERATOR_A: ClassVar[UUID] = UUID("01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e60")
    OPERATOR_B: ClassVar[UUID] = UUID("01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e70")
    UNKNOWN_OPERATOR: ClassVar[UUID] = UUID("01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e90")
    PERSON_ID: ClassVar[UUID] = UUID("01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e62")
    EVENT_A1: ClassVar[UUID] = UUID("01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e81")
    EVENT_A2: ClassVar[UUID] = UUID("01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e82")
    EVENT_B1: ClassVar[UUID] = UUID("01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e83")
    EVENT_TYPE: ClassVar[str] = "fleet.drone_registered"
    OCCURRED_AT: ClassVar[datetime] = datetime(2026, 11, 19, 10, 30, 15, 123456, tzinfo=UTC)
    PAYLOAD: ClassVar[Dict[str, JsonValue]] = {"name": "Scout", "slots": [1, 2]}

    def build(self, event_id: UUID, operator_id: UUID) -> Event:
        return Event(
            id=event_id,
            type=self.EVENT_TYPE,
            operator_id=operator_id,
            occurred_at=self.OCCURRED_AT,
            actor=Actor(kind=ActorKind.PERSON, person_id=self.PERSON_ID),
            payload=dict(self.PAYLOAD),
        )

    @pytest.fixture
    async def service(self, monkeypatch: pytest.MonkeyPatch, postgres_dsn: str) -> AsyncIterator[EventService]:
        monkeypatch.setenv(FleetConfig.DSN_KEY, postgres_dsn)
        config = FleetConfig()
        await SchemaServiceFactory(config).create().upgrade()
        events = EventServiceFactory(config).create()
        await events.open()
        yield events
        await events.close()

    async def record_all(self, service: EventService) -> List[Event]:
        events = [
            self.build(self.EVENT_A1, self.OPERATOR_A),
            self.build(self.EVENT_B1, self.OPERATOR_B),
            self.build(self.EVENT_A2, self.OPERATOR_A),
        ]
        for event in events:
            await service.record(event)
        return events

    def test_a_fleet_event_has_no_mission(self) -> None:
        assert self.build(self.EVENT_A1, self.OPERATOR_A).mission_id is None

    async def test_record_returns_the_event(self, service: EventService) -> None:
        event = self.build(self.EVENT_A1, self.OPERATOR_A)
        assert await service.record(event) == event

    async def test_pending_returns_only_the_events_of_operator_a(self, service: EventService) -> None:
        a1, _, a2 = await self.record_all(service)
        assert await service.pending(self.OPERATOR_A) == [a1, a2]

    async def test_pending_returns_only_the_events_of_operator_b(self, service: EventService) -> None:
        _, b1, _ = await self.record_all(service)
        assert await service.pending(self.OPERATOR_B) == [b1]

    @pytest.mark.parametrize("operator_id", [None, UNKNOWN_OPERATOR])
    async def test_pending_without_a_known_operator_returns_nothing(
        self, service: EventService, operator_id: Optional[UUID]
    ) -> None:
        await self.record_all(service)
        assert await service.pending(operator_id) == []

    async def test_close_is_safe_twice(self, service: EventService) -> None:
        await service.close()
        await service.close()
