from __future__ import annotations

# Standard library imports
from typing import AsyncIterator, ClassVar, List

# Third-party imports
import asyncpg
import pytest

# First-party imports
from missions.models.config.missions_config import MissionsConfig
from missions.service.factories.schema_service_factory import SchemaServiceFactory
from missions.service.schema.schema_service import SchemaService
from swarm_storage.shared.postgres.ddl.outbox_table import OutboxTable
from swarm_storage.shared.postgres.ddl.row_level_security import RowLevelSecurity


class TestMissionsSchemaService:
    REVISION: ClassVar[str] = "0001"
    SECURITY_QUERY: ClassVar[str] = (
        "SELECT c.relrowsecurity, c.relforcerowsecurity FROM pg_class c "
        "JOIN pg_namespace n ON n.oid = c.relnamespace WHERE n.nspname = $1 AND c.relname = $2"
    )
    POLICY_QUERY: ClassVar[str] = "SELECT policyname FROM pg_policies WHERE schemaname = $1 AND tablename = $2"
    TABLE_QUERY: ClassVar[str] = "SELECT to_regclass($1) IS NOT NULL"

    @pytest.fixture
    async def service(self, postgres_dsn: str, monkeypatch: pytest.MonkeyPatch) -> AsyncIterator[SchemaService]:
        monkeypatch.setenv(MissionsConfig.DSN_KEY, postgres_dsn)
        yield SchemaServiceFactory(MissionsConfig()).create()

    async def rows(self, dsn: str, query: str, *arguments: str) -> List[asyncpg.Record]:
        connection = await asyncpg.connect(dsn)
        try:
            return list(await connection.fetch(query, *arguments))
        except asyncpg.PostgresError as error:
            raise AssertionError(f"The check query failed: {type(error).__name__}.") from error
        finally:
            await connection.close()

    async def table_exists(self, dsn: str) -> bool:
        qualified = f"{MissionsConfig().schema_name}.{OutboxTable.TABLE}"
        return bool((await self.rows(dsn, self.TABLE_QUERY, qualified))[0][0])

    async def security_flags(self, dsn: str) -> List[bool]:
        rows = await self.rows(dsn, self.SECURITY_QUERY, MissionsConfig().schema_name, OutboxTable.TABLE)
        return [rows[0][0], rows[0][1]]

    async def policies(self, dsn: str) -> List[str]:
        rows = await self.rows(dsn, self.POLICY_QUERY, MissionsConfig().schema_name, OutboxTable.TABLE)
        return [row[0] for row in rows]

    async def test_upgrade_creates_the_outbox_with_row_level_security(
        self, service: SchemaService, postgres_dsn: str
    ) -> None:
        await service.upgrade()
        assert await self.table_exists(postgres_dsn)
        assert await self.security_flags(postgres_dsn) == [True, True]
        assert await self.policies(postgres_dsn) == [RowLevelSecurity.POLICY_NAME]

    async def test_current_is_the_first_revision_after_an_upgrade(self, service: SchemaService) -> None:
        await service.upgrade()
        assert await service.current() == self.REVISION

    async def test_current_is_none_before_an_upgrade(self, service: SchemaService) -> None:
        assert await service.current() is None

    async def test_a_second_upgrade_changes_nothing(self, service: SchemaService, postgres_dsn: str) -> None:
        await service.upgrade()
        await service.upgrade()
        assert await service.current() == self.REVISION
        assert await self.policies(postgres_dsn) == [RowLevelSecurity.POLICY_NAME]

    async def test_downgrade_to_base_drops_the_table(self, service: SchemaService, postgres_dsn: str) -> None:
        await service.upgrade()
        await service.downgrade_to_base()
        assert not await self.table_exists(postgres_dsn)
        assert await service.current() is None
