from __future__ import annotations

# Standard library imports
from logging import Logger, getLogger
from pathlib import Path
from typing import Optional

# First-party imports
from swarm_lifecycle.factories.async_runnable_factory import AsyncRunnableFactory
from swarm_models.config.postgres.postgres_config import PostgresConfig
from swarm_service.shared.migrations.factories.schema_service_factory import SchemaServiceFactory
from swarm_service.shared.migrations.schema_migration import SchemaMigration


class SchemaMigrationFactory(AsyncRunnableFactory[SchemaMigration]):
    """Builds the migration that upgrades the schema of an app.

    Attributes:
        postgres (PostgresConfig): The connection pool settings of the app, whose status interval the migration takes.
        schema_name (str): The PostgreSQL schema of the app.
        migrations_folder (Path): The folder of the Alembic migrations of the app.
    """

    def __init__(
        self, postgres: PostgresConfig, schema_name: str, migrations_folder: Path, logger: Optional[Logger] = None
    ) -> None:
        """Prepare the factory.

        Args:
            postgres (PostgresConfig): The connection pool settings of the app.
            schema_name (str): The PostgreSQL schema of the app.
            migrations_folder (Path): The folder of the Alembic migrations of the app.
            logger (Optional[Logger]): Logger instance.
        """
        super().__init__()
        self.logger = logger if logger else getLogger(__name__)
        self.postgres = postgres
        self.schema_name = schema_name
        self.migrations_folder = migrations_folder

    ############################
    # Internal Helpers Methods #
    ############################

    def _build(self) -> SchemaMigration:
        """Build one migration.

        Returns:
            SchemaMigration: A new migration on a new schema service.
        """
        self.logger.debug("Building a migration of schema %s.", self.schema_name)
        service = SchemaServiceFactory(self.postgres, self.schema_name, self.migrations_folder).create()
        return SchemaMigration(service, self.postgres.status_interval_s)
