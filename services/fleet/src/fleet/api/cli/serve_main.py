from __future__ import annotations

# First-party imports
from fleet.api.rest.fleet_rest_app import FleetRestApp
from fleet.models.config.fleet_config import FleetConfig
from swarm_logging.configurators.logging_configurator import LoggingConfigurator
from swarm_logging.models.logging_config import LoggingConfig
from swarm_rest.api.factories.async_runnable_runner_factory import AsyncRunnableRunnerFactory
from swarm_rest.api.factories.rest_server_factory import RestServerFactory


def main() -> None:
    """Configure logging once, then serve the application until it is stopped.

    Notes:
        - Logging is configured once, here at the entry point.
    """
    folder = FleetConfig.conf_folder()
    config = FleetConfig.load(folder / FleetConfig.APP_FILE)
    LoggingConfigurator(LoggingConfig(path=str(folder / FleetConfig.LOGGER_FILE))).configure()
    app = FleetRestApp(config).build()
    server = RestServerFactory(app, config.rest).create()
    AsyncRunnableRunnerFactory(server).create().execute()
