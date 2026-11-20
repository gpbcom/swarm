from __future__ import annotations

# Standard library imports
from logging import Logger, getLogger
from typing import Optional

# First-party imports
from missions.api.cli.commands.migrate_command import MigrateCommand
from missions.models.config.missions_config import MissionsConfig
from missions.service.factories.schema_service_factory import SchemaServiceFactory
from swarm_lifecycle.factories.async_runnable_factory import AsyncRunnableFactory


class MigrateCommandFactory(AsyncRunnableFactory[MigrateCommand]):
    """Builds migrate commands.

    Attributes:
        config (MissionsConfig): The settings of the service.
    """

    def __init__(self, config: MissionsConfig, logger: Optional[Logger] = None) -> None:
        """Initialise the factory.

        Args:
            config (MissionsConfig): The settings of the service.
            logger (Optional[Logger]): Logger to use. A logger named after the module is used when it is ``None``.
        """
        super().__init__()
        self.logger = logger if logger else getLogger(__name__)
        self.config = config

    ############################
    # Internal Helpers Methods #
    ############################

    def _build(self) -> MigrateCommand:
        """Build one command.

        Returns:
            MigrateCommand: A command on the schema service of the configuration, with its status interval.
        """
        self.logger.debug("Building a migrate command.")
        schema = SchemaServiceFactory(self.config).create()
        return MigrateCommand(schema, self.config.postgres.status_interval_s)
