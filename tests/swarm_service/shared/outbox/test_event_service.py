from __future__ import annotations

# Standard library imports
from datetime import UTC, datetime
from pathlib import Path
from typing import AsyncIterator, ClassVar, List, Optional
from uuid import UUID

# Third-party imports
import pytest

# First-party imports
from swarm_models.config.gateway.gateway_config import GatewayConfig
from swarm_models.events.actor import Actor
from swarm_models.events.enums import ActorKind
from swarm_models.events.event import Event
from swarm_service.shared.migrations.factories.schema_service_factory import SchemaServiceFactory
from swarm_service.shared.outbox.event_service import EventService
from swarm_service.shared.outbox.factories.event_service_factory import EventServiceFactory


class TestEventService:
    MIGRATIONS: ClassVar[Path] = Path(__file__).resolve().parents[4] / "backend" / "apps" / "gateway" / "migrations"
    OPERATOR_A: ClassVar[UUID] = UUID("01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e60")
    OPERATOR_B: ClassVar[UUID] = UUID("01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e61")
    PERSON_ID: ClassVar[UUID] = UUID("01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e62")
    EVENT_A1: ClassVar[UUID] = UUID("01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e71")
    EVENT_A2: ClassVar[UUID] = UUID("01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e72")
    EVENT_B1: ClassVar[UUID] = UUID("01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e73")
    EVENT_B2: ClassVar[UUID] = UUID("01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e74")
    OCCURRED_AT: ClassVar[datetime] = datetime(2026, 11, 19, 10, 30, 15, 123456, tzinfo=UTC)
    EVENT_TYPE: ClassVar[str] = "operator.created"
    PENDING_LIMIT: ClassVar[int] = 100

    def an_event(self, event_id: UUID, operator_id: UUID) -> Event:
        return Event(
            id=event_id,
            type=self.EVENT_TYPE,
            operator_id=operator_id,
            occurred_at=self.OCCURRED_AT,
            actor=Actor(kind=ActorKind.PERSON, person_id=self.PERSON_ID),
            payload={},
        )

    @pytest.fixture
    async def service(self, postgres_dsn: str, monkeypatch: pytest.MonkeyPatch) -> AsyncIterator[EventService]:
        monkeypatch.setenv(GatewayConfig.DSN_KEY, postgres_dsn)
        config = GatewayConfig()
        await SchemaServiceFactory(config.postgres, config.schema_name, self.MIGRATIONS).create().upgrade()
        event_service = EventServiceFactory(config.postgres, config.schema_name).create()
        await event_service.open()
        for event in (
            self.an_event(self.EVENT_A1, self.OPERATOR_A),
            self.an_event(self.EVENT_A2, self.OPERATOR_A),
            self.an_event(self.EVENT_B1, self.OPERATOR_B),
        ):
            await event_service.record(event)
        yield event_service
        await event_service.close()

    @pytest.mark.parametrize(
        ("operator_id", "expected"),
        [
            (OPERATOR_A, [EVENT_A1, EVENT_A2]),
            (OPERATOR_B, [EVENT_B1]),
        ],
    )
    async def test_an_operator_only_sees_its_own_events(
        self, service: EventService, operator_id: UUID, expected: List[UUID]
    ) -> None:
        events = await service.pending(operator_id, self.PENDING_LIMIT)
        assert sorted(event.id for event in events) == sorted(expected)
        assert {event.operator_id for event in events} == {operator_id}

    async def test_a_query_that_forgets_the_operator_returns_nothing(self, service: EventService) -> None:
        forgotten: Optional[UUID] = None
        assert await service.pending(forgotten) == []

    async def test_record_returns_the_event_it_stored(self, service: EventService) -> None:
        event = self.an_event(self.EVENT_B2, self.OPERATOR_B)
        assert await service.record(event) == event
        assert self.EVENT_B2 in {stored.id for stored in await service.pending(self.OPERATOR_B)}

    async def test_close_is_safe_twice(self, service: EventService) -> None:
        await service.close()
        await service.close()
