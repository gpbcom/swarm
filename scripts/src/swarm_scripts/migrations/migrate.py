from __future__ import annotations

# Standard library imports
from logging import getLogger

# First-party imports
from gateway.api.factories.migrate.migrate_command_factory import MigrateCommandFactory
from gateway.models.config.gateway_config import GatewayConfig
from swarm_logging.configurators.logging_configurator import LoggingConfigurator
from swarm_logging.models.logging_config import LoggingConfig
from swarm_rest.api.factories.async_runnable_runner_factory import AsyncRunnableRunnerFactory


def main() -> None:
    """Configure logging, then migrate the schema.

    Raises:
        SystemExit: When the migration failed.
    """
    config = GatewayConfig.load(GatewayConfig.conf_folder() / GatewayConfig.APP_FILE)
    LoggingConfigurator(LoggingConfig(path=str(GatewayConfig.conf_folder() / GatewayConfig.LOGGER_FILE))).configure()
    command = MigrateCommandFactory(config).create()
    AsyncRunnableRunnerFactory(command).create().execute()
    if command.exit_code != 0:
        getLogger(__name__).error("The migrate command ended with exit code %d.", command.exit_code)
        raise SystemExit(command.exit_code)
