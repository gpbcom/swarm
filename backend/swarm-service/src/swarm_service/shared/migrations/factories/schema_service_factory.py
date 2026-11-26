from __future__ import annotations

# Standard library imports
from logging import Logger, getLogger
from pathlib import Path
from typing import Optional

# First-party imports
from swarm_lifecycle.factories.factory import Factory
from swarm_models.config.postgres.postgres_config import PostgresConfig
from swarm_service.shared.migrations.schema_service import SchemaService
from swarm_storage.shared.postgres.migrations.alembic_migrator import AlembicMigrator


class SchemaServiceFactory(Factory[SchemaService]):
    """Builds the schema service of an app from its PostgreSQL settings and its migrations.

    Attributes:
        postgres (PostgresConfig): The connection pool settings of the app.
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

    def _build(self) -> SchemaService:
        """Build one schema service on the migrations folder of the app.

        Returns:
            SchemaService: A new service.
        """
        self.logger.debug("Building a schema service on schema %s.", self.schema_name)
        migrator = AlembicMigrator(self.postgres, self.schema_name, self.migrations_folder)
        return SchemaService(migrator)
