from __future__ import annotations

# Standard library imports
from logging import getLogger

# First-party imports
from swarm_api.v1.fleet.fleet_router import FleetRouter
from swarm_logging.configurators.logging_configurator import LoggingConfigurator
from swarm_logging.models.logging_config import LoggingConfig
from swarm_models.config.fleet.fleet_config import FleetConfig
from swarm_web.factories.async_runnable_runner_factory import AsyncRunnableRunnerFactory
from swarm_web.factories.rest_server_factory import RestServerFactory
from swarm_web.signals.signals_configurator import SignalsConfigurator


def main() -> None:
    """Read the configuration of the fleet app, configure logging and signals, then serve the app until it is stopped.

    Notes:
        - The app's folder is ``SWARM_APP_ROOT``, which the image sets, or the current folder.
        - Logging is configured once, here at the entry point, then the OpenTelemetry signals.
    """
    folder = FleetConfig.conf_folder()
    config = FleetConfig.load(folder / FleetConfig.APP_FILE)
    LoggingConfigurator(LoggingConfig(path=str(folder / FleetConfig.LOGGER_FILE))).configure()
    SignalsConfigurator(config.signals).configure()
    getLogger(__name__).info("Serving the fleet app on port %d.", config.rest.port)
    server = RestServerFactory(FleetRouter(config).application(), config.rest).create()
    AsyncRunnableRunnerFactory(server).create().execute()
