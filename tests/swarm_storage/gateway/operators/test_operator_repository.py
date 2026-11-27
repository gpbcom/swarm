from __future__ import annotations

# Standard library imports
from typing import AsyncIterator, ClassVar, List
from uuid import UUID

# Third-party imports
import asyncpg
import pytest

# First-party imports
from swarm_models.config.postgres.postgres_config import PostgresConfig
from swarm_models.enums import Anchoring, Deployment, Jurisdiction, LlmProvider
from swarm_models.operators.operator import Operator
from swarm_models.storage.exceptions import SEStorageDuplicateError
from swarm_storage.gateway.ddl.operator_directory_tables import OperatorDirectoryTables
from swarm_storage.gateway.operators.operator_repository import OperatorRepository
from swarm_storage.shared.postgres.postgres_pool import PostgresPool
from swarm_storage.shared.postgres.repositories.postgres_repository import PostgresRepository


class TestOperatorRepository:
    SCHEMA: ClassVar[str] = "directory"
    SETUP_SCHEMA: ClassVar[str] = "CREATE SCHEMA directory"
    OPERATOR_A: ClassVar[UUID] = UUID("01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e60")
    OPERATOR_B: ClassVar[UUID] = UUID("01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e61")
    MISSING: ClassVar[UUID] = UUID("01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e7f")
    NAME_A: ClassVar[str] = "Aerowing Services"
    NAME_B: ClassVar[str] = "Bluesky Surveys"
    SAME_NAME_VARIANTS: ClassVar[List[str]] = ["aerowing services", "AEROWING SERVICES", "  Aerowing Services  "]

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

    def operator(self, operator_id: UUID, name: str) -> Operator:
        return Operator(
            id=operator_id,
            name=name,
            deployment=Deployment.ON_PREMISES,
            jurisdictions=[Jurisdiction.EU_EASA, Jurisdiction.US_FAA],
            llm_provider=LlmProvider.OPEN_WEIGHT,
            anchoring=Anchoring.PUBLIC_BLOCKCHAIN,
        )

    def test_it_is_a_postgres_repository(self) -> None:
        assert issubclass(OperatorRepository, PostgresRepository)

    async def test_an_operator_round_trips_with_every_field(self, pool: PostgresPool) -> None:
        operator = self.operator(self.OPERATOR_A, self.NAME_A)
        async with pool.unit_of_work(None) as uow:
            repository = OperatorRepository(uow, self.SCHEMA)
            assert await repository.add(operator) == operator
            found = await repository.get(self.OPERATOR_A)
        assert found == operator
        assert found is not None
        assert found.jurisdictions == [Jurisdiction.EU_EASA, Jurisdiction.US_FAA]

    async def test_an_unknown_operator_is_not_found(self, pool: PostgresPool) -> None:
        async with pool.unit_of_work(None) as uow:
            assert await OperatorRepository(uow, self.SCHEMA).get(self.MISSING) is None

    async def test_list_returns_every_operator_ordered_by_id(self, pool: PostgresPool) -> None:
        async with pool.unit_of_work(None) as uow:
            repository = OperatorRepository(uow, self.SCHEMA)
            await repository.add(self.operator(self.OPERATOR_B, self.NAME_B))
            await repository.add(self.operator(self.OPERATOR_A, self.NAME_A))
            assert [item.id for item in await repository.list()] == [self.OPERATOR_A, self.OPERATOR_B]

    async def test_find_by_name_matches_without_case_and_spaces(self, pool: PostgresPool) -> None:
        operator = self.operator(self.OPERATOR_A, self.NAME_A)
        async with pool.unit_of_work(None) as uow:
            repository = OperatorRepository(uow, self.SCHEMA)
            await repository.add(operator)
            for name in [self.NAME_A, *self.SAME_NAME_VARIANTS]:
                assert await repository.find_by_name(name) == operator

    async def test_find_by_name_returns_none_for_an_unknown_name(self, pool: PostgresPool) -> None:
        async with pool.unit_of_work(None) as uow:
            repository = OperatorRepository(uow, self.SCHEMA)
            await repository.add(self.operator(self.OPERATOR_A, self.NAME_A))
            assert await repository.find_by_name(self.NAME_B) is None

    @pytest.mark.parametrize("name", SAME_NAME_VARIANTS)
    async def test_a_second_operator_with_the_same_name_is_refused(self, pool: PostgresPool, name: str) -> None:
        async with pool.unit_of_work(None) as uow:
            repository = OperatorRepository(uow, self.SCHEMA)
            await repository.add(self.operator(self.OPERATOR_A, self.NAME_A))
            with pytest.raises(SEStorageDuplicateError):
                await repository.add(self.operator(self.OPERATOR_B, name))
