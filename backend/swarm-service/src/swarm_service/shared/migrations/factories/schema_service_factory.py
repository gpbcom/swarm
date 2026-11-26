from __future__ import annotations

# Standard library imports
from logging import Logger, getLogger
from typing import Optional

# First-party imports
from gateway.models.config.gateway_config import GatewayConfig
from gateway.service.schema.schema_service import SchemaService
from swarm_lifecycle.factories.factory import Factory
from swarm_storage.shared.postgres.migrations.alembic_migrator import AlembicMigrator


class SchemaServiceFactory(Factory[SchemaService]):
    """Builds the schema service of the gateway from its configuration.

    Attributes:
        config (GatewayConfig): The configuration of the gateway.
    """

    def __init__(self, config: GatewayConfig, logger: Optional[Logger] = None) -> None:
        """Prepare the factory.

        Args:
            config (GatewayConfig): The configuration of the gateway.
            logger (Optional[Logger]): Logger instance.
        """
        super().__init__()
        self.logger = logger if logger else getLogger(__name__)
        self.config = config

    ############################
    # Internal Helpers Methods #
    ############################

    def _build(self) -> SchemaService:
        """Build one schema service on the migrations folder of the gateway.

        Returns:
            SchemaService: A new service.
        """
        self.logger.debug("Building a schema service on schema %s.", self.config.schema_name)
        migrator = AlembicMigrator(self.config.postgres, self.config.schema_name, GatewayConfig.migrations_folder())
        return SchemaService(migrator)
