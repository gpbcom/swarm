from __future__ import annotations

# Standard library imports
from logging import getLogger

# First-party imports
from swarm_api.v1.gateway.gateway_router import GatewayRouter
from swarm_logging.configurators.logging_configurator import LoggingConfigurator
from swarm_logging.models.logging_config import LoggingConfig
from swarm_models.config.gateway.gateway_config import GatewayConfig
from swarm_web.factories.async_runnable_runner_factory import AsyncRunnableRunnerFactory
from swarm_web.factories.rest_server_factory import RestServerFactory


def main() -> None:
    """Read the configuration of the gateway app, configure logging, then serve the app until it is stopped.

    Notes:
        - The app's folder is ``SWARM_APP_ROOT``, which the image sets, or the current folder.
        - Logging is configured once, here at the entry point.
    """
    folder = GatewayConfig.conf_folder()
    config = GatewayConfig.load(folder / GatewayConfig.APP_FILE)
    LoggingConfigurator(LoggingConfig(path=str(folder / GatewayConfig.LOGGER_FILE))).configure()
    getLogger(__name__).info("Serving the gateway app on port %d.", config.rest.port)
    server = RestServerFactory(GatewayRouter(config).application(), config.rest).create()
    AsyncRunnableRunnerFactory(server).create().execute()
