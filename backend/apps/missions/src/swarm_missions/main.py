from __future__ import annotations

# Standard library imports
from logging import getLogger

# First-party imports
from missions.api.rest.missions_rest_app import MissionsRestApp
from missions.models.config.missions_config import MissionsConfig
from swarm_logging.configurators.logging_configurator import LoggingConfigurator
from swarm_logging.models.logging_config import LoggingConfig
from swarm_rest.api.factories.async_runnable_runner_factory import AsyncRunnableRunnerFactory
from swarm_web.factories.rest_server_factory import RestServerFactory


def main() -> None:
    """Configure logging, then serve the application until it is stopped."""
    config = MissionsConfig.load(MissionsConfig.conf_folder() / MissionsConfig.APP_FILE)
    logger_path = MissionsConfig.conf_folder() / MissionsConfig.LOGGER_FILE
    LoggingConfigurator(LoggingConfig(path=str(logger_path))).configure()
    app = MissionsRestApp(config).build()
    server = RestServerFactory(app, config.rest).create()
    getLogger(__name__).info("Serving the missions API on port %d.", config.rest.port)
    AsyncRunnableRunnerFactory(server).create().execute()
