from __future__ import annotations

# Standard library imports
from logging import Logger, getLogger
from typing import Optional

# First-party imports
from missions.models.config.missions_config import MissionsConfig
from missions.service.schema.schema_service import SchemaService
from swarm_lifecycle.factories.factory import Factory
from swarm_storage.shared.postgres.migrations.alembic_migrator import AlembicMigrator


class SchemaServiceFactory(Factory[SchemaService]):
    """Builds schema services, bound to the migrations of the service.

    Attributes:
        config (MissionsConfig): The settings the schema and the DSN entry come from.
    """

    def __init__(self, config: MissionsConfig, logger: Optional[Logger] = None) -> None:
        """Initialise the factory.

        Args:
            config (MissionsConfig): The settings the schema and the DSN entry come from.
            logger (Optional[Logger]): Logger to use. A logger named after the module is used when it is ``None``.
        """
        super().__init__()
        self.logger = logger if logger else getLogger(__name__)
        self.config = config

    ############################
    # Internal Helpers Methods #
    ############################

    def _build(self) -> SchemaService:
        """Build one service on the migrations folder ``services/missions/migrations``.

        Returns:
            SchemaService: A service for the schema of the configuration.
        """
        folder = MissionsConfig.migrations_folder()
        migrator = AlembicMigrator(self.config.postgres, self.config.schema_name, folder)
        self.logger.debug("Built a migrator for schema %s.", self.config.schema_name)
        return SchemaService(migrator)
