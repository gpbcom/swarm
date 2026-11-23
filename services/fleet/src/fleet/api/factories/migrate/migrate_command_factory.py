from __future__ import annotations

# Standard library imports
from logging import Logger, getLogger
from typing import Optional

# First-party imports
from fleet.api.cli.commands.migrate_command import MigrateCommand
from fleet.models.config.fleet_config import FleetConfig
from fleet.service.factories.schema_service_factory import SchemaServiceFactory
from swarm_lifecycle.factories.async_runnable_factory import AsyncRunnableFactory


class MigrateCommandFactory(AsyncRunnableFactory[MigrateCommand]):
    """Builds migrate commands on the PostgreSQL settings of the fleet service.

    Attributes:
        config (FleetConfig): The settings the commands come from.
    """

    def __init__(self, config: FleetConfig, logger: Optional[Logger] = None) -> None:
        """Initialise the factory.

        Args:
            config (FleetConfig): The settings the commands come from.
            logger (Optional[Logger]): Logger to use. A logger named after the module is used when it is ``None``.
        """
        super().__init__()
        self.logger = logger if logger else getLogger(__name__)
        self.config = config

    ############################
    # Internal Helpers Methods #
    ############################

    def _build(self) -> MigrateCommand:
        """Build one command with a new schema service.

        Returns:
            MigrateCommand: A command whose status interval is the one of the PostgreSQL settings.
        """
        self.logger.debug("Building a migrate command for schema %s.", self.config.schema_name)
        service = SchemaServiceFactory(self.config).create()
        return MigrateCommand(self.config.postgres.status_interval_s, service)
