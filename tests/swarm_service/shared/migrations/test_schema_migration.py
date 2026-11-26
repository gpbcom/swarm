from __future__ import annotations

# Standard library imports
import subprocess
from pathlib import Path
from typing import ClassVar, List

# Third-party imports
import pytest

# First-party imports
from swarm_lifecycle.models.enums import RunnableStatus
from swarm_lifecycle.runnables.async_runnable import AsyncRunnable
from swarm_models.config.gateway.gateway_config import GatewayConfig
from swarm_service.shared.migrations.factories.schema_migration_factory import SchemaMigrationFactory
from swarm_service.shared.migrations.schema_migration import SchemaMigration


class TestSchemaMigration:
    MIGRATIONS: ClassVar[Path] = Path(__file__).resolve().parents[4] / "backend" / "apps" / "gateway" / "migrations"
    PSQL: ClassVar[str] = "psql"
    PSQL_FLAGS: ClassVar[List[str]] = ["-X", "-q", "-At", "-v", "ON_ERROR_STOP=1", "-c"]
    OUTBOX_QUERY: ClassVar[str] = "SELECT to_regclass('gateway.outbox') IS NOT NULL"
    TRUE_OUTPUT: ClassVar[str] = "t"
    ENCODING: ClassVar[str] = "utf-8"

    def outbox_exists(self, dsn: str) -> bool:
        result = subprocess.run(
            [self.PSQL, dsn, *self.PSQL_FLAGS, self.OUTBOX_QUERY],
            capture_output=True,
            text=True,
            encoding=self.ENCODING,
            check=True,
        )
        return result.stdout.strip() == self.TRUE_OUTPUT

    def migration(self) -> SchemaMigration:
        config = GatewayConfig()
        return SchemaMigrationFactory(config.postgres, config.schema_name, self.MIGRATIONS).create()

    def test_the_migration_is_an_async_runnable(self) -> None:
        assert isinstance(self.migration(), AsyncRunnable)

    async def test_the_migration_creates_the_outbox_and_exits_with_zero(
        self, monkeypatch: pytest.MonkeyPatch, postgres_dsn: str
    ) -> None:
        monkeypatch.setenv(GatewayConfig.DSN_KEY, postgres_dsn)
        migration = self.migration()

        statuses = [status async for status in migration.execute()]

        assert statuses[-1] == RunnableStatus.EXECUTED
        assert migration.exit_code == 0
        assert self.outbox_exists(postgres_dsn)

    async def test_without_a_dsn_the_migration_exits_with_one_and_raises_nothing(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv(GatewayConfig.DSN_KEY, raising=False)
        migration = self.migration()

        statuses = [status async for status in migration.execute()]

        assert RunnableStatus.EXECUTED not in statuses
        assert migration.exit_code == 1
