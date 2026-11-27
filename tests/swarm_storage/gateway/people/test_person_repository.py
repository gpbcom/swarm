from __future__ import annotations

# Standard library imports
from typing import AsyncIterator, ClassVar, Optional
from uuid import UUID

# Third-party imports
import asyncpg
import pytest

# First-party imports
from swarm_models.config.postgres.postgres_config import PostgresConfig
from swarm_models.enums import Language
from swarm_models.people.person import Person
from swarm_models.storage.exceptions import SEStorageOperatorRefusedError
from swarm_storage.gateway.ddl.operator_directory_tables import OperatorDirectoryTables
from swarm_storage.gateway.people.person_repository import PersonRepository
from swarm_storage.shared.postgres.postgres_pool import PostgresPool


class TestPersonRepository:
    SCHEMA: ClassVar[str] = "directory"
    SETUP_SCHEMA: ClassVar[str] = "CREATE SCHEMA directory"
    OPERATOR_A: ClassVar[UUID] = UUID("01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e60")
    OPERATOR_B: ClassVar[UUID] = UUID("01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e61")
    PERSON_A: ClassVar[UUID] = UUID("01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e62")
    PERSON_B: ClassVar[UUID] = UUID("01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e63")
    EMAIL_A: ClassVar[str] = "ada@a.example"
    EMAIL_B: ClassVar[str] = "bob@b.example"

    @pytest.fixture
    async def pool(self, monkeypatch: pytest.MonkeyPatch, postgres_dsn: str) -> AsyncIterator[PostgresPool]:
        config = PostgresConfig()
        monkeypatch.setenv(config.dsn_key, postgres_dsn)
        connection = await asyncpg.connect(postgres_dsn)
        await connection.execute(self.SETUP_SCHEMA)
        for statement in OperatorDirectoryTables().create(self.SCHEMA):
            await connection.execute(statement)
        await connection.close()
        pool = PostgresPool(config)
        await pool.open()
        yield pool
        await pool.close()

    def person(self, person_id: UUID, operator_id: Optional[UUID], email: str) -> Person:
        return Person(id=person_id, operator_id=operator_id, name="Ada Planner", email=email, language=Language.FRENCH)

    async def seed(self, pool: PostgresPool) -> None:
        async with pool.unit_of_work(self.OPERATOR_A) as uow:
            await PersonRepository(uow, self.SCHEMA).add(self.person(self.PERSON_A, self.OPERATOR_A, self.EMAIL_A))
        async with pool.unit_of_work(self.OPERATOR_B) as uow:
            await PersonRepository(uow, self.SCHEMA).add(self.person(self.PERSON_B, self.OPERATOR_B, self.EMAIL_B))

    async def test_a_person_round_trips_in_the_unit_of_work_of_its_operator(self, pool: PostgresPool) -> None:
        person = self.person(self.PERSON_A, self.OPERATOR_A, self.EMAIL_A)
        async with pool.unit_of_work(self.OPERATOR_A) as uow:
            repository = PersonRepository(uow, self.SCHEMA)
            assert await repository.add(person) == person
            assert await repository.get(self.PERSON_A) == person
            assert await repository.list() == [person]

    async def test_a_person_of_operator_a_is_invisible_to_operator_b(self, pool: PostgresPool) -> None:
        await self.seed(pool)
        async with pool.unit_of_work(self.OPERATOR_B) as uow:
            repository = PersonRepository(uow, self.SCHEMA)
            assert await repository.get(self.PERSON_A) is None
            assert [item.id for item in await repository.list()] == [self.PERSON_B]

    async def test_a_query_without_an_operator_returns_no_person(self, pool: PostgresPool) -> None:
        await self.seed(pool)
        async with pool.unit_of_work(None) as uow:
            repository = PersonRepository(uow, self.SCHEMA)
            assert await repository.get(self.PERSON_A) is None
            assert await repository.list() == []

    async def test_adding_a_person_of_another_operator_is_refused(self, pool: PostgresPool) -> None:
        other = self.person(self.PERSON_B, self.OPERATOR_B, self.EMAIL_B)
        async with pool.unit_of_work(self.OPERATOR_A) as uow:
            with pytest.raises(SEStorageOperatorRefusedError):
                await PersonRepository(uow, self.SCHEMA).add(other)
