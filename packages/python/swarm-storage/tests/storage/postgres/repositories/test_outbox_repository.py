from __future__ import annotations

from datetime import UTC, datetime
from typing import AsyncIterator, ClassVar, Dict, List, Optional
from uuid import UUID

import asyncpg
import pytest
from pydantic import JsonValue

from swarm_models.models.events.actor import Actor
from swarm_models.models.events.enums import ActorKind
from swarm_models.models.events.event import Event
from swarm_storage.models.config.postgres_config import PostgresConfig
from swarm_storage.models.postgres.exceptions import (
    SEStorageInvalidPageError,
    SEStorageOperatorRefusedError,
    SEStorageVersionConflictError,
)
from swarm_storage.storage.postgres.ddl.outbox_table import OutboxTable
from swarm_storage.storage.postgres.postgres_pool import PostgresPool
from swarm_storage.storage.postgres.repositories.outbox_repository import OutboxRepository
from swarm_storage.storage.postgres.repositories.postgres_repository import PostgresRepository


class TestOutboxRepository:
    SCHEMA: ClassVar[str] = "demo"
    SETUP_SCHEMA: ClassVar[str] = "CREATE SCHEMA demo"
    OPERATOR_A: ClassVar[UUID] = UUID("01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e60")
    OPERATOR_B: ClassVar[UUID] = UUID("01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e61")
    PERSON_ID: ClassVar[UUID] = UUID("01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e62")
    EVENT_1: ClassVar[UUID] = UUID("01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e71")
    EVENT_2: ClassVar[UUID] = UUID("01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e72")
    EVENT_3: ClassVar[UUID] = UUID("01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e73")
    EVENT_OTHER: ClassVar[UUID] = UUID("01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e74")
    MISSING: ClassVar[UUID] = UUID("01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e7f")
    EVENT_TYPE: ClassVar[str] = "mission.planned"
    OCCURRED_AT: ClassVar[datetime] = datetime(2026, 11, 19, 10, 30, 15, 123456, tzinfo=UTC)
    PAYLOAD: ClassVar[Dict[str, JsonValue]] = {"name": "Survey"}
    PAYLOAD_CHANGED: ClassVar[Dict[str, JsonValue]] = {"name": "Survey again"}

    @pytest.fixture
    async def pool(self, monkeypatch: pytest.MonkeyPatch, postgres_dsn: str) -> AsyncIterator[PostgresPool]:
        config = PostgresConfig()
        monkeypatch.setenv(config.dsn_key, postgres_dsn)
        connection = await asyncpg.connect(postgres_dsn)
        await connection.execute(self.SETUP_SCHEMA)
        for statement in OutboxTable().create(self.SCHEMA):
            await connection.execute(statement)
        await connection.close()
        pool = PostgresPool(config)
        await pool.open()
        yield pool
        await pool.close()

    def event(self, event_id: UUID, operator_id: UUID, payload: Optional[Dict[str, JsonValue]] = None) -> Event:
        return Event(
            id=event_id,
            type=self.EVENT_TYPE,
            operator_id=operator_id,
            occurred_at=self.OCCURRED_AT,
            actor=Actor(kind=ActorKind.PERSON, person_id=self.PERSON_ID),
            payload=payload if payload else self.PAYLOAD,
        )

    async def seed(self, pool: PostgresPool) -> None:
        async with pool.unit_of_work(self.OPERATOR_A) as uow:
            repository = OutboxRepository(uow, self.SCHEMA)
            for event_id in (self.EVENT_1, self.EVENT_2, self.EVENT_3):
                await repository.add(self.event(event_id, self.OPERATOR_A))
        async with pool.unit_of_work(self.OPERATOR_B) as uow:
            await OutboxRepository(uow, self.SCHEMA).add(self.event(self.EVENT_OTHER, self.OPERATOR_B))

    def test_it_is_a_postgres_repository(self) -> None:
        assert issubclass(OutboxRepository, PostgresRepository)

    async def test_add_returns_the_event(self, pool: PostgresPool) -> None:
        event = self.event(self.EVENT_1, self.OPERATOR_A)
        async with pool.unit_of_work(self.OPERATOR_A) as uow:
            assert await OutboxRepository(uow, self.SCHEMA).add(event) == event

    async def test_get_returns_the_event_of_its_own_operator_only(self, pool: PostgresPool) -> None:
        await self.seed(pool)
        async with pool.unit_of_work(self.OPERATOR_A) as uow:
            repository = OutboxRepository(uow, self.SCHEMA)
            assert await repository.get(self.EVENT_1) == self.event(self.EVENT_1, self.OPERATOR_A)
            assert await repository.get(self.EVENT_OTHER) is None

    async def test_list_is_ordered_by_id_and_pages_after_an_id(self, pool: PostgresPool) -> None:
        await self.seed(pool)
        async with pool.unit_of_work(self.OPERATOR_A) as uow:
            repository = OutboxRepository(uow, self.SCHEMA)
            assert [item.id for item in await repository.list()] == [self.EVENT_1, self.EVENT_2, self.EVENT_3]
            rest = await repository.list(after=self.EVENT_1)
            assert [item.id for item in rest] == [self.EVENT_2, self.EVENT_3]
            assert [item.id for item in await repository.list(limit=1)] == [self.EVENT_1]

    @pytest.mark.parametrize("limit", [0, -1, PostgresRepository.PAGE_SIZE_MAX + 1])
    async def test_a_limit_out_of_range_is_refused(self, pool: PostgresPool, limit: int) -> None:
        async with pool.unit_of_work(self.OPERATOR_A) as uow:
            repository = OutboxRepository(uow, self.SCHEMA)
            with pytest.raises(SEStorageInvalidPageError):
                await repository.list(limit=limit)

    async def test_pending_returns_the_unpublished_events_in_recording_order(self, pool: PostgresPool) -> None:
        await self.seed(pool)
        async with pool.unit_of_work(self.OPERATOR_A) as uow:
            repository = OutboxRepository(uow, self.SCHEMA)
            assert [item.id for item in await repository.pending()] == [self.EVENT_1, self.EVENT_2, self.EVENT_3]

    async def test_mark_published_removes_the_event_from_pending(self, pool: PostgresPool) -> None:
        await self.seed(pool)
        async with pool.unit_of_work(self.OPERATOR_A) as uow:
            repository = OutboxRepository(uow, self.SCHEMA)
            assert await repository.mark_published(self.EVENT_1) is True
            assert [item.id for item in await repository.pending()] == [self.EVENT_2, self.EVENT_3]

    async def test_mark_published_returns_false_for_another_operators_event(self, pool: PostgresPool) -> None:
        await self.seed(pool)
        async with pool.unit_of_work(self.OPERATOR_A) as uow:
            assert await OutboxRepository(uow, self.SCHEMA).mark_published(self.EVENT_OTHER) is False
        async with pool.unit_of_work(self.OPERATOR_B) as uow:
            pending = await OutboxRepository(uow, self.SCHEMA).pending()
            assert [item.id for item in pending] == [self.EVENT_OTHER]

    async def test_version_starts_at_one_and_update_increments_it(self, pool: PostgresPool) -> None:
        await self.seed(pool)
        async with pool.unit_of_work(self.OPERATOR_A) as uow:
            repository = OutboxRepository(uow, self.SCHEMA)
            assert await repository.version_of(self.EVENT_1) == 1
            changed = self.event(self.EVENT_1, self.OPERATOR_A, self.PAYLOAD_CHANGED)
            assert await repository.update(changed, expected_version=1) == 2
            assert await repository.version_of(self.EVENT_1) == 2
            assert await repository.get(self.EVENT_1) == changed

    async def test_an_update_with_a_stale_version_is_refused(self, pool: PostgresPool) -> None:
        await self.seed(pool)
        async with pool.unit_of_work(self.OPERATOR_A) as uow:
            repository = OutboxRepository(uow, self.SCHEMA)
            changed = self.event(self.EVENT_1, self.OPERATOR_A, self.PAYLOAD_CHANGED)
            await repository.update(changed, expected_version=1)
            with pytest.raises(SEStorageVersionConflictError):
                await repository.update(changed, expected_version=1)

    async def test_an_update_of_another_operators_row_is_refused(self, pool: PostgresPool) -> None:
        await self.seed(pool)
        async with pool.unit_of_work(self.OPERATOR_A) as uow:
            repository = OutboxRepository(uow, self.SCHEMA)
            other = self.event(self.EVENT_OTHER, self.OPERATOR_A, self.PAYLOAD_CHANGED)
            with pytest.raises(SEStorageVersionConflictError):
                await repository.update(other, expected_version=1)

    async def test_delete_removes_the_event(self, pool: PostgresPool) -> None:
        await self.seed(pool)
        async with pool.unit_of_work(self.OPERATOR_A) as uow:
            repository = OutboxRepository(uow, self.SCHEMA)
            assert await repository.delete(self.EVENT_1) is True
            assert await repository.get(self.EVENT_1) is None
            assert await repository.delete(self.MISSING) is False

    async def test_a_query_without_an_operator_returns_nothing(self, pool: PostgresPool) -> None:
        await self.seed(pool)
        async with pool.unit_of_work(None) as uow:
            repository = OutboxRepository(uow, self.SCHEMA)
            assert await repository.pending() == []
            assert await repository.list() == []

    async def test_a_query_never_returns_another_operators_events(self, pool: PostgresPool) -> None:
        await self.seed(pool)
        async with pool.unit_of_work(self.OPERATOR_A) as uow:
            repository = OutboxRepository(uow, self.SCHEMA)
            found: List[Event] = [*await repository.pending(), *await repository.list()]
            assert found
            assert all(item.operator_id == self.OPERATOR_A for item in found)

    async def test_adding_another_operators_event_is_refused(self, pool: PostgresPool) -> None:
        async with pool.unit_of_work(self.OPERATOR_A) as uow:
            with pytest.raises(SEStorageOperatorRefusedError):
                await OutboxRepository(uow, self.SCHEMA).add(self.event(self.EVENT_OTHER, self.OPERATOR_B))
