from __future__ import annotations

# Standard library imports
from logging import Logger, getLogger
from typing import Optional

# First-party imports
from gateway.api.cli.commands.migrate_command import MigrateCommand
from gateway.models.config.gateway_config import GatewayConfig
from gateway.service.factories.schema_service_factory import SchemaServiceFactory
from swarm_lifecycle.factories.async_runnable_factory import AsyncRunnableFactory


class MigrateCommandFactory(AsyncRunnableFactory[MigrateCommand]):
    """Builds the command that migrates the schema of the gateway.

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

    def _build(self) -> MigrateCommand:
        """Build one migrate command.

        Returns:
            MigrateCommand: A new command on a new schema service.
        """
        self.logger.debug("Building a migrate command.")
        service = SchemaServiceFactory(self.config).create()
        return MigrateCommand(service, self.config.postgres.status_interval_s)
