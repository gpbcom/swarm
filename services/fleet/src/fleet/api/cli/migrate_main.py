from __future__ import annotations

# Standard library imports
from logging import getLogger

# First-party imports
from fleet.api.factories.migrate.migrate_command_factory import MigrateCommandFactory
from fleet.models.config.fleet_config import FleetConfig
from swarm_logging.configurators.logging_configurator import LoggingConfigurator
from swarm_logging.models.logging_config import LoggingConfig
from swarm_rest.api.factories.async_runnable_runner_factory import AsyncRunnableRunnerFactory


def main() -> None:
    """Configure logging once, then upgrade the schema.

    Raises:
        SystemExit: When the exit code of the command is not 0.

    Notes:
        - Logging is configured once, here at the entry point.
    """
    folder = FleetConfig.conf_folder()
    config = FleetConfig.load(folder / FleetConfig.APP_FILE)
    LoggingConfigurator(LoggingConfig(path=str(folder / FleetConfig.LOGGER_FILE))).configure()
    command = MigrateCommandFactory(config).create()
    AsyncRunnableRunnerFactory(command).create().execute()
    if command.exit_code != 0:
        getLogger(__name__).error("The migrate command ended with exit code %d.", command.exit_code)
        raise SystemExit(command.exit_code)
