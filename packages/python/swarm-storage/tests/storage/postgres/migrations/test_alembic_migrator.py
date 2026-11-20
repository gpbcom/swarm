from __future__ import annotations

from pathlib import Path
from typing import ClassVar, Optional

import asyncpg
import pytest

from swarm_storage.models.config.postgres_config import PostgresConfig
from swarm_storage.models.postgres.exceptions import SEStorageDsnMissingError, SEStorageMigrationError
from swarm_storage.storage.postgres.ddl.outbox_table import OutboxTable
from swarm_storage.storage.postgres.migrations.alembic_migrator import AlembicMigrator


class TestAlembicMigrator:
    SCHEMA: ClassVar[str] = "demo"
    REVISION: ClassVar[str] = "0001"
    BASE: ClassVar[str] = "base"
    VERSION_TABLE: ClassVar[str] = "alembic_version"
    SAMPLE: ClassVar[Path] = Path(__file__).parent / "sample"
    SCHEMA_QUERY: ClassVar[str] = "SELECT count(*) FROM pg_namespace WHERE nspname = $1"
    TABLE_QUERY: ClassVar[str] = "SELECT count(*) FROM pg_tables WHERE schemaname = $1 AND tablename = $2"

    @pytest.fixture
    def config(self, monkeypatch: pytest.MonkeyPatch, postgres_dsn: str) -> PostgresConfig:
        config = PostgresConfig()
        monkeypatch.setenv(config.dsn_key, postgres_dsn)
        return config

    def migrator(self, config: PostgresConfig, script_location: Optional[Path] = None) -> AlembicMigrator:
        return AlembicMigrator(config, self.SCHEMA, script_location if script_location else self.SAMPLE)

    async def count(self, dsn: str, query: str, *args: str) -> int:
        connection = await asyncpg.connect(dsn)
        value = await connection.fetchval(query, *args)
        await connection.close()
        return int(value)

    async def test_upgrade_creates_the_schema_and_the_outbox(self, config: PostgresConfig, postgres_dsn: str) -> None:
        assert await self.count(postgres_dsn, self.SCHEMA_QUERY, self.SCHEMA) == 0
        await self.migrator(config).upgrade()
        assert await self.count(postgres_dsn, self.SCHEMA_QUERY, self.SCHEMA) == 1
        assert await self.count(postgres_dsn, self.TABLE_QUERY, self.SCHEMA, OutboxTable.TABLE) == 1

    async def test_current_is_the_applied_revision(self, config: PostgresConfig) -> None:
        migrator = self.migrator(config)
        assert await migrator.current() is None
        await migrator.upgrade()
        assert await migrator.current() == self.REVISION

    async def test_a_second_upgrade_changes_nothing(self, config: PostgresConfig, postgres_dsn: str) -> None:
        migrator = self.migrator(config)
        await migrator.upgrade()
        await migrator.upgrade()
        assert await migrator.current() == self.REVISION
        assert await self.count(postgres_dsn, self.TABLE_QUERY, self.SCHEMA, OutboxTable.TABLE) == 1

    async def test_the_version_table_lives_in_the_given_schema(self, config: PostgresConfig, postgres_dsn: str) -> None:
        await self.migrator(config).upgrade()
        assert await self.count(postgres_dsn, self.TABLE_QUERY, self.SCHEMA, self.VERSION_TABLE) == 1

    async def test_downgrade_to_base_drops_the_outbox(self, config: PostgresConfig, postgres_dsn: str) -> None:
        migrator = self.migrator(config)
        await migrator.upgrade()
        await migrator.downgrade(self.BASE)
        assert await self.count(postgres_dsn, self.TABLE_QUERY, self.SCHEMA, OutboxTable.TABLE) == 0
        assert await migrator.current() is None

    async def test_a_missing_script_folder_is_refused(self, config: PostgresConfig, tmp_path: Path) -> None:
        with pytest.raises(SEStorageMigrationError):
            await self.migrator(config, tmp_path / "missing").upgrade()

    async def test_an_unset_dsn_is_refused(self, config: PostgresConfig, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv(config.dsn_key, raising=False)
        with pytest.raises(SEStorageDsnMissingError):
            await self.migrator(config).upgrade()
