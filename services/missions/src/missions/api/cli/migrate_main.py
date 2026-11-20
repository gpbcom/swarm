from __future__ import annotations

# Standard library imports
from logging import getLogger

# First-party imports
from missions.api.factories.migrate.migrate_command_factory import MigrateCommandFactory
from missions.models.config.missions_config import MissionsConfig
from swarm_logging.configurators.logging_configurator import LoggingConfigurator
from swarm_logging.models.logging_config import LoggingConfig
from swarm_rest.api.factories.async_runnable_runner_factory import AsyncRunnableRunnerFactory


def main() -> None:
    """Configure logging, then apply the migrations.

    Raises:
        SystemExit: When the migration fails.
    """
    config = MissionsConfig.load(MissionsConfig.conf_folder() / MissionsConfig.APP_FILE)
    logger_path = MissionsConfig.conf_folder() / MissionsConfig.LOGGER_FILE
    LoggingConfigurator(LoggingConfig(path=str(logger_path))).configure()
    logger = getLogger(__name__)
    command = MigrateCommandFactory(config).create()
    AsyncRunnableRunnerFactory(command).create().execute()
    if command.exit_code != command.EXIT_OK:
        logger.error("The migration ended with exit code %d.", command.exit_code)
        raise SystemExit(command.exit_code)
    logger.debug("The migration ended with exit code %d.", command.exit_code)
