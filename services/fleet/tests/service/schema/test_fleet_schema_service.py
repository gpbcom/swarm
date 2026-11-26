from __future__ import annotations

# Standard library imports
from typing import ClassVar

# Third-party imports
import asyncpg
import pytest

# First-party imports
from fleet.models.config.fleet_config import FleetConfig
from fleet.service.factories.schema_service_factory import SchemaServiceFactory
from fleet.service.schema.schema_service import SchemaService
from swarm_storage.shared.postgres.ddl.row_level_security import RowLevelSecurity


class TestFleetSchemaService:
    TABLE_FLAGS_SQL: ClassVar[str] = (
        "SELECT c.relrowsecurity, c.relforcerowsecurity FROM pg_class c "
        "JOIN pg_namespace n ON n.oid = c.relnamespace WHERE n.nspname = $1 AND c.relname = $2"
    )
    POLICY_SQL: ClassVar[str] = "SELECT policyname FROM pg_policies WHERE schemaname = $1 AND tablename = $2"
    TABLE_EXISTS_SQL: ClassVar[str] = "SELECT to_regclass($1) IS NOT NULL"
    OUTBOX: ClassVar[str] = "outbox"
    FIRST_REVISION: ClassVar[str] = "0001"

    @pytest.fixture
    def service(self, monkeypatch: pytest.MonkeyPatch, postgres_dsn: str) -> SchemaService:
        monkeypatch.setenv(FleetConfig.DSN_KEY, postgres_dsn)
        return SchemaServiceFactory(FleetConfig()).create()

    async def table_exists(self, dsn: str) -> bool:
        connection = await asyncpg.connect(dsn)
        try:
            return bool(await connection.fetchval(self.TABLE_EXISTS_SQL, f"{FleetConfig().schema_name}.{self.OUTBOX}"))
        except asyncpg.PostgresError as error:
            pytest.fail(f"Query failed: {type(error).__name__}.")
        finally:
            await connection.close()

    async def test_upgrade_creates_the_outbox_with_row_level_security(
        self, service: SchemaService, postgres_dsn: str
    ) -> None:
        await service.upgrade()
        schema = FleetConfig().schema_name
        connection = await asyncpg.connect(postgres_dsn)
        try:
            flags = await connection.fetchrow(self.TABLE_FLAGS_SQL, schema, self.OUTBOX)
            policies = await connection.fetch(self.POLICY_SQL, schema, self.OUTBOX)
        except asyncpg.PostgresError as error:
            pytest.fail(f"Query failed: {type(error).__name__}.")
        finally:
            await connection.close()
        assert flags is not None
        assert flags["relrowsecurity"] is True
        assert flags["relforcerowsecurity"] is True
        assert [row["policyname"] for row in policies] == [RowLevelSecurity.POLICY_NAME]

    async def test_current_is_the_first_revision_after_the_upgrade(self, service: SchemaService) -> None:
        assert await service.current() is None
        await service.upgrade()
        assert await service.current() == self.FIRST_REVISION

    async def test_a_second_upgrade_changes_nothing(self, service: SchemaService, postgres_dsn: str) -> None:
        await service.upgrade()
        await service.upgrade()
        assert await service.current() == self.FIRST_REVISION
        assert await self.table_exists(postgres_dsn)

    async def test_downgrade_to_base_drops_the_table(self, service: SchemaService, postgres_dsn: str) -> None:
        await service.upgrade()
        assert await self.table_exists(postgres_dsn)
        await service.downgrade_to_base()
        assert not await self.table_exists(postgres_dsn)
        assert await service.current() is None
