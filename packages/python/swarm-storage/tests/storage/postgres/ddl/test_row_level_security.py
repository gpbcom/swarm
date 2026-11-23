from __future__ import annotations

# Standard library imports
from typing import AsyncIterator, ClassVar, List
from uuid import UUID

# Third-party imports
import asyncpg
import pytest
from pytest import MonkeyPatch

# First-party imports
from swarm_storage.models.config.postgres_config import PostgresConfig
from swarm_storage.models.postgres.exceptions import SEStorageInvalidIdentifierError
from swarm_storage.storage.postgres.ddl.row_level_security import RowLevelSecurity
from swarm_storage.storage.postgres.postgres_pool import PostgresPool
from swarm_storage.storage.postgres.unit_of_work import UnitOfWork


class TestRowLevelSecurity:
    OPERATOR_A: ClassVar[UUID] = UUID("01890a5d-ac96-774b-bcce-b302099a8057")
    OPERATOR_B: ClassVar[UUID] = UUID("01890a5d-ac96-7b3c-8d1e-4f5a6b7c8d9e")
    ROW_A: ClassVar[UUID] = UUID("01890a5d-ac96-7c00-8000-000000000001")
    ROW_B: ClassVar[UUID] = UUID("01890a5d-ac96-7c00-8000-000000000002")
    SCHEMA: ClassVar[str] = "demo"
    TABLE: ClassVar[str] = "items"
    OPERATOR_COLUMN: ClassVar[str] = "operator_id"
    CREATE_SCHEMA: ClassVar[str] = "CREATE SCHEMA demo"
    CREATE_TABLE: ClassVar[str] = "CREATE TABLE demo.items (id uuid primary key, operator_id uuid not null)"
    INSERT: ClassVar[str] = "INSERT INTO demo.items (id, operator_id) VALUES ($1, $2)"
    SELECT_ALL: ClassVar[str] = "SELECT operator_id FROM demo.items"

    @pytest.fixture
    async def pool(self, monkeypatch: MonkeyPatch, postgres_dsn: str) -> AsyncIterator[PostgresPool]:
        monkeypatch.setenv(PostgresConfig().dsn_key, postgres_dsn)
        connection = await asyncpg.connect(postgres_dsn)
        await self.execute_statements(connection, [self.CREATE_SCHEMA, self.CREATE_TABLE])
        await self.execute_statements(connection, RowLevelSecurity().enable(self.SCHEMA, self.TABLE))
        await connection.close()
        opened = PostgresPool(PostgresConfig())
        await opened.open()
        yield opened
        await opened.close()

    async def execute_statements(self, connection: asyncpg.Connection, statements: List[str]) -> None:
        for statement in statements:
            await connection.execute(statement)

    async def insert_both(self, pool: PostgresPool) -> None:
        async with pool.unit_of_work(self.OPERATOR_A) as uow:
            await uow.connection.execute(self.INSERT, self.ROW_A, self.OPERATOR_A)
        async with pool.unit_of_work(self.OPERATOR_B) as uow:
            await uow.connection.execute(self.INSERT, self.ROW_B, self.OPERATOR_B)

    def test_enable_returns_the_three_statements_in_order(self) -> None:
        statements = RowLevelSecurity().enable(self.SCHEMA, self.TABLE)
        assert len(statements) == 3
        assert "ENABLE ROW LEVEL SECURITY" in statements[0]
        assert "FORCE ROW LEVEL SECURITY" in statements[1]
        assert "CREATE POLICY" in statements[2]
        assert RowLevelSecurity.POLICY_NAME in statements[2]
        assert UnitOfWork.OPERATOR_SETTING in statements[2]
        assert self.OPERATOR_COLUMN in statements[2]

    def test_disable_undoes_the_enable_statements(self) -> None:
        joined = " ".join(RowLevelSecurity().disable(self.SCHEMA, self.TABLE))
        assert RowLevelSecurity.POLICY_NAME in joined
        assert "DISABLE ROW LEVEL SECURITY" in joined

    @pytest.mark.parametrize("name", ["", "Demo", "1a", "x;drop"])
    def test_an_invalid_identifier_is_refused(self, name: str) -> None:
        with pytest.raises(SEStorageInvalidIdentifierError):
            RowLevelSecurity().enable(name, self.TABLE)
        with pytest.raises(SEStorageInvalidIdentifierError):
            RowLevelSecurity().enable(self.SCHEMA, name)
        with pytest.raises(SEStorageInvalidIdentifierError):
            RowLevelSecurity().disable(name, self.TABLE)

    async def test_a_query_without_the_operator_filter_returns_only_its_own_rows(self, pool: PostgresPool) -> None:
        await self.insert_both(pool)
        async with pool.unit_of_work(self.OPERATOR_A) as uow:
            rows = await uow.connection.fetch(self.SELECT_ALL)
            assert [row[self.OPERATOR_COLUMN] for row in rows] == [self.OPERATOR_A]
        async with pool.unit_of_work(None) as uow:
            assert await uow.connection.fetch(self.SELECT_ALL) == []

    async def test_inserting_a_row_of_another_operator_is_refused(self, pool: PostgresPool) -> None:
        with pytest.raises(asyncpg.exceptions.InsufficientPrivilegeError):
            async with pool.unit_of_work(self.OPERATOR_A) as uow:
                await uow.connection.execute(self.INSERT, self.ROW_B, self.OPERATOR_B)

    async def test_after_disable_both_rows_are_visible(self, pool: PostgresPool) -> None:
        await self.insert_both(pool)
        async with pool.unit_of_work(None) as uow:
            await self.execute_statements(uow.connection, RowLevelSecurity().disable(self.SCHEMA, self.TABLE))
        async with pool.unit_of_work(self.OPERATOR_A) as uow:
            rows = await uow.connection.fetch(self.SELECT_ALL)
            assert {row[self.OPERATOR_COLUMN] for row in rows} == {self.OPERATOR_A, self.OPERATOR_B}
