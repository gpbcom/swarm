from __future__ import annotations

# Standard library imports
from pathlib import Path
from typing import ClassVar

# First-party imports
from swarm_lifecycle.factories.async_runnable_factory import AsyncRunnableFactory
from swarm_models.config.gateway.gateway_config import GatewayConfig
from swarm_service.shared.migrations.factories.schema_migration_factory import SchemaMigrationFactory
from swarm_service.shared.migrations.schema_migration import SchemaMigration


class TestSchemaMigrationFactory:
    MIGRATIONS: ClassVar[Path] = Path(__file__).resolve().parents[5] / "backend" / "apps" / "gateway" / "migrations"

    def factory(self) -> SchemaMigrationFactory:
        config = GatewayConfig()
        return SchemaMigrationFactory(config.postgres, config.schema_name, self.MIGRATIONS)

    def test_create_returns_a_migration_with_the_configured_status_interval(self) -> None:
        migration = self.factory().create()

        assert isinstance(migration, SchemaMigration)
        assert migration.status_interval_s == GatewayConfig().postgres.status_interval_s

    def test_the_factory_is_an_async_runnable_factory(self) -> None:
        assert isinstance(self.factory(), AsyncRunnableFactory)

    def test_create_returns_a_new_migration_on_each_call(self) -> None:
        factory = self.factory()

        assert factory.create() is not factory.create()
