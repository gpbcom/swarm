from __future__ import annotations

# Standard library imports
from pathlib import Path
from typing import ClassVar, List

# Third-party imports
import asyncpg
import pytest

# First-party imports
from swarm_models.config.gateway.gateway_config import GatewayConfig
from swarm_service.shared.migrations.factories.schema_service_factory import SchemaServiceFactory
from swarm_service.shared.migrations.schema_service import SchemaService
from swarm_storage.shared.postgres.ddl.row_level_security import RowLevelSecurity


class TestSchemaService:
    MIGRATIONS: ClassVar[Path] = Path(__file__).resolve().parents[4] / "backend" / "apps" / "gateway" / "migrations"
    REVISION: ClassVar[str] = "0001"
    TABLE_NAME: ClassVar[str] = "outbox"
    TABLE_QUERY: ClassVar[str] = (
        "SELECT c.relrowsecurity, c.relforcerowsecurity FROM pg_class c "
        "JOIN pg_namespace n ON n.oid = c.relnamespace WHERE n.nspname = $1 AND c.relname = $2"
    )
    POLICY_QUERY: ClassVar[str] = "SELECT policyname FROM pg_policies WHERE schemaname = $1 AND tablename = $2"
    ROW_SECURITY_COLUMN: ClassVar[str] = "relrowsecurity"
    FORCE_ROW_SECURITY_COLUMN: ClassVar[str] = "relforcerowsecurity"
    POLICY_COLUMN: ClassVar[str] = "policyname"

    @pytest.fixture
    def service(self, postgres_dsn: str, monkeypatch: pytest.MonkeyPatch) -> SchemaService:
        monkeypatch.setenv(GatewayConfig.DSN_KEY, postgres_dsn)
        config = GatewayConfig()
        return SchemaServiceFactory(config.postgres, config.schema_name, self.MIGRATIONS).create()

    async def table_flags(self, dsn: str) -> List[asyncpg.Record]:
        connection = await asyncpg.connect(dsn)
        rows = await connection.fetch(self.TABLE_QUERY, GatewayConfig().schema_name, self.TABLE_NAME)
        await connection.close()
        return rows

    async def policies(self, dsn: str) -> List[str]:
        connection = await asyncpg.connect(dsn)
        rows = await connection.fetch(self.POLICY_QUERY, GatewayConfig().schema_name, self.TABLE_NAME)
        await connection.close()
        return [row[self.POLICY_COLUMN] for row in rows]

    async def test_upgrade_creates_the_outbox_with_row_level_security(
        self, service: SchemaService, postgres_dsn: str
    ) -> None:
        await service.upgrade()
        rows = await self.table_flags(postgres_dsn)
        assert len(rows) == 1
        assert rows[0][self.ROW_SECURITY_COLUMN] is True
        assert rows[0][self.FORCE_ROW_SECURITY_COLUMN] is True
        assert await self.policies(postgres_dsn) == [RowLevelSecurity.POLICY_NAME]

    async def test_current_is_the_first_revision_after_the_upgrade(self, service: SchemaService) -> None:
        assert await service.current() is None
        await service.upgrade()
        assert await service.current() == self.REVISION

    async def test_a_second_upgrade_changes_nothing(self, service: SchemaService, postgres_dsn: str) -> None:
        await service.upgrade()
        await service.upgrade()
        assert await service.current() == self.REVISION
        assert len(await self.table_flags(postgres_dsn)) == 1
        assert await self.policies(postgres_dsn) == [RowLevelSecurity.POLICY_NAME]

    async def test_downgrade_to_base_drops_the_table(self, service: SchemaService, postgres_dsn: str) -> None:
        await service.upgrade()
        await service.downgrade_to_base()
        assert await self.table_flags(postgres_dsn) == []
        assert await service.current() is None
