from __future__ import annotations

# Standard library imports
from typing import AsyncIterator, ClassVar, Dict

# Third-party imports
import asyncpg
import pytest

# First-party imports
from swarm_storage.models.postgres.exceptions import SEStorageInvalidIdentifierError
from swarm_storage.storage.postgres.ddl.outbox_table import OutboxTable
from swarm_storage.storage.postgres.ddl.row_level_security import RowLevelSecurity


class TestOutboxTable:
    SCHEMA: ClassVar[str] = "outbox_demo"
    CREATE_SCHEMA: ClassVar[str] = "CREATE SCHEMA outbox_demo"
    RLS_FLAGS: ClassVar[str] = "SELECT relrowsecurity, relforcerowsecurity FROM pg_class WHERE oid = to_regclass($1)"
    POLICIES: ClassVar[str] = "SELECT policyname FROM pg_policies WHERE schemaname = $1 AND tablename = $2"
    COLUMNS: ClassVar[str] = (
        "SELECT column_name, data_type, is_nullable FROM information_schema.columns "
        "WHERE table_schema = $1 AND table_name = $2"
    )
    REGCLASS: ClassVar[str] = "SELECT to_regclass($1)"
    EXPECTED_TYPES: ClassVar[Dict[str, str]] = {
        "id": "uuid",
        "operator_id": "uuid",
        "version": "integer",
        "event": "jsonb",
        "recorded_at": "timestamp with time zone",
        "published_at": "timestamp with time zone",
    }
    NULLABLE_COLUMN: ClassVar[str] = "published_at"
    INDEX_COLUMNS: ClassVar[str] = "(operator_id, id)"

    @pytest.fixture
    async def raw(self, postgres_dsn: str) -> AsyncIterator[asyncpg.Connection]:
        connection = await asyncpg.connect(postgres_dsn)
        await connection.execute(self.CREATE_SCHEMA)
        for statement in OutboxTable().create(self.SCHEMA):
            await connection.execute(statement)
        yield connection
        await connection.close()

    def test_create_returns_statements_for_the_table_its_index_and_its_policy(self) -> None:
        statements = OutboxTable().create(self.SCHEMA)
        joined = "\n".join(statements)
        assert f"{self.SCHEMA}.{OutboxTable.TABLE}" in joined
        assert self.INDEX_COLUMNS in joined
        for statement in RowLevelSecurity().enable(self.SCHEMA, OutboxTable.TABLE):
            assert statement in statements

    def test_drop_names_the_table(self) -> None:
        statements = OutboxTable().drop(self.SCHEMA)
        assert any(f"{self.SCHEMA}.{OutboxTable.TABLE}" in statement for statement in statements)

    @pytest.mark.parametrize("schema", ["", "Demo", "1a", "x;drop"])
    def test_an_invalid_schema_is_refused(self, schema: str) -> None:
        with pytest.raises(SEStorageInvalidIdentifierError):
            OutboxTable().create(schema)
        with pytest.raises(SEStorageInvalidIdentifierError):
            OutboxTable().drop(schema)

    async def test_create_builds_a_protected_table_with_the_expected_columns(self, raw: asyncpg.Connection) -> None:
        qualified = f"{self.SCHEMA}.{OutboxTable.TABLE}"
        flags = await raw.fetchrow(self.RLS_FLAGS, qualified)
        assert flags is not None
        assert flags["relrowsecurity"] is True
        assert flags["relforcerowsecurity"] is True
        policies = await raw.fetch(self.POLICIES, self.SCHEMA, OutboxTable.TABLE)
        assert [row["policyname"] for row in policies] == [RowLevelSecurity.POLICY_NAME]
        columns = await raw.fetch(self.COLUMNS, self.SCHEMA, OutboxTable.TABLE)
        assert {row["column_name"]: row["data_type"] for row in columns} == self.EXPECTED_TYPES
        nullable = {row["column_name"] for row in columns if row["is_nullable"] == "YES"}
        assert nullable == {self.NULLABLE_COLUMN}

    async def test_drop_removes_the_table_from_the_database(self, raw: asyncpg.Connection) -> None:
        for statement in OutboxTable().drop(self.SCHEMA):
            await raw.execute(statement)
        assert await raw.fetchval(self.REGCLASS, f"{self.SCHEMA}.{OutboxTable.TABLE}") is None
