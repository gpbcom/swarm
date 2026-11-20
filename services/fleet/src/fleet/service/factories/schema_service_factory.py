from __future__ import annotations

# Standard library imports
from logging import Logger, getLogger
from pathlib import Path
from typing import ClassVar, Optional

# First-party imports
from fleet.models.config.fleet_config import FleetConfig
from fleet.service.schema.schema_service import SchemaService
from swarm_lifecycle.factories.factory import Factory
from swarm_storage.storage.postgres.migrations.alembic_migrator import AlembicMigrator


class SchemaServiceFactory(Factory[SchemaService]):
    """Builds schema services on the migrations folder of the fleet service.

    Attributes:
        MIGRATIONS_FOLDER_NAME (str): The name of the migrations folder, in the service folder.
        config (FleetConfig): The settings the migrator comes from.
    """

    MIGRATIONS_FOLDER_NAME: ClassVar[str] = "migrations"

    def __init__(self, config: FleetConfig, logger: Optional[Logger] = None) -> None:
        """Initialise the factory.

        Args:
            config (FleetConfig): The settings the migrator comes from.
            logger (Optional[Logger]): Logger to use. A logger named after the module is used when it is ``None``.
        """
        super().__init__()
        self.logger = logger if logger else getLogger(__name__)
        self.config = config

    ############################
    # Internal Helpers Methods #
    ############################

    def _build(self) -> SchemaService:
        """Build one service with a new migrator.

        Returns:
            SchemaService: A service on the schema of the configuration.
        """
        folder: Path = FleetConfig.conf_folder().parent / self.MIGRATIONS_FOLDER_NAME
        migrator = AlembicMigrator(self.config.postgres, self.config.schema_name, folder)
        self.logger.debug("Built a migrator for schema %s.", self.config.schema_name)
        return SchemaService(migrator)
