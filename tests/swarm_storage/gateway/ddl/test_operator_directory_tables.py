from __future__ import annotations

# Standard library imports
from typing import AsyncIterator, ClassVar, Dict, List

# Third-party imports
import asyncpg
import pytest

# First-party imports
from swarm_models.storage.exceptions import SEStorageInvalidIdentifierError
from swarm_storage.gateway.ddl.operator_directory_tables import OperatorDirectoryTables
from swarm_storage.shared.postgres.ddl.row_level_security import RowLevelSecurity


class TestOperatorDirectoryTables:
    SCHEMA: ClassVar[str] = "directory_demo"
    CREATE_SCHEMA: ClassVar[str] = "CREATE SCHEMA directory_demo"
    GLOBAL_TABLES: ClassVar[List[str]] = ["operators", "cell_assignments"]
    PROTECTED_TABLE: ClassVar[str] = "people"
    ALL_TABLES: ClassVar[List[str]] = ["operators", "cell_assignments", "people"]
    RLS_FLAGS: ClassVar[str] = "SELECT relrowsecurity FROM pg_class WHERE oid = to_regclass($1)"
    POLICIES: ClassVar[str] = "SELECT policyname FROM pg_policies WHERE schemaname = $1 AND tablename = $2"
    REGCLASS: ClassVar[str] = "SELECT to_regclass($1)"
    COLUMN_NAMES: ClassVar[str] = (
        "SELECT column_name FROM information_schema.columns WHERE table_schema = $1 AND table_name = $2"
    )
    KEY_COLUMNS: ClassVar[Dict[str, str]] = {
        "operators": "id",
        "cell_assignments": "operator_id",
        "people": "operator_id",
    }

    @pytest.fixture
    async def raw(self, postgres_dsn: str) -> AsyncIterator[asyncpg.Connection]:
        connection = await asyncpg.connect(postgres_dsn)
        await connection.execute(self.CREATE_SCHEMA)
        for statement in OperatorDirectoryTables().create(self.SCHEMA):
            await connection.execute(statement)
        yield connection
        await connection.close()

    def test_create_names_the_three_tables(self) -> None:
        joined = "\n".join(OperatorDirectoryTables().create(self.SCHEMA))
        for table in self.ALL_TABLES:
            assert f"{self.SCHEMA}.{table}" in joined

    def test_only_the_people_table_has_row_level_security_statements(self) -> None:
        statements = OperatorDirectoryTables().create(self.SCHEMA)
        for statement in RowLevelSecurity().enable(self.SCHEMA, self.PROTECTED_TABLE):
            assert statement in statements
        for table in self.GLOBAL_TABLES:
            for statement in RowLevelSecurity().enable(self.SCHEMA, table):
                assert statement not in statements

    def test_drop_names_the_three_tables(self) -> None:
        joined = "\n".join(OperatorDirectoryTables().drop(self.SCHEMA))
        for table in self.ALL_TABLES:
            assert f"{self.SCHEMA}.{table}" in joined

    @pytest.mark.parametrize("schema", ["", "Demo", "1a", "x;drop"])
    def test_an_invalid_schema_is_refused(self, schema: str) -> None:
        with pytest.raises(SEStorageInvalidIdentifierError):
            OperatorDirectoryTables().create(schema)
        with pytest.raises(SEStorageInvalidIdentifierError):
            OperatorDirectoryTables().drop(schema)

    async def test_the_tables_have_their_key_column(self, raw: asyncpg.Connection) -> None:
        for table, column in self.KEY_COLUMNS.items():
            rows = await raw.fetch(self.COLUMN_NAMES, self.SCHEMA, table)
            assert column in {row["column_name"] for row in rows}

    async def test_the_global_tables_have_no_row_level_security(self, raw: asyncpg.Connection) -> None:
        for table in self.GLOBAL_TABLES:
            assert await raw.fetchval(self.RLS_FLAGS, f"{self.SCHEMA}.{table}") is False
            assert await raw.fetch(self.POLICIES, self.SCHEMA, table) == []

    async def test_the_people_table_has_row_level_security(self, raw: asyncpg.Connection) -> None:
        assert await raw.fetchval(self.RLS_FLAGS, f"{self.SCHEMA}.{self.PROTECTED_TABLE}") is True
        policies = await raw.fetch(self.POLICIES, self.SCHEMA, self.PROTECTED_TABLE)
        assert [row["policyname"] for row in policies] == [RowLevelSecurity.POLICY_NAME]

    async def test_drop_removes_the_three_tables(self, raw: asyncpg.Connection) -> None:
        for statement in OperatorDirectoryTables().drop(self.SCHEMA):
            await raw.execute(statement)
        for table in self.ALL_TABLES:
            assert await raw.fetchval(self.REGCLASS, f"{self.SCHEMA}.{table}") is None
