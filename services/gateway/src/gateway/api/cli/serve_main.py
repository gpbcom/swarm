from __future__ import annotations

# Standard library imports
from logging import getLogger

# First-party imports
from gateway.api.rest.gateway_rest_app import GatewayRestApp
from gateway.models.config.gateway_config import GatewayConfig
from swarm_logging.configurators.logging_configurator import LoggingConfigurator
from swarm_logging.models.logging_config import LoggingConfig
from swarm_rest.api.factories.async_runnable_runner_factory import AsyncRunnableRunnerFactory
from swarm_web.factories.rest_server_factory import RestServerFactory


def main() -> None:
    """Configure logging, then serve the gateway until it is stopped."""
    config = GatewayConfig.load(GatewayConfig.conf_folder() / GatewayConfig.APP_FILE)
    LoggingConfigurator(LoggingConfig(path=str(GatewayConfig.conf_folder() / GatewayConfig.LOGGER_FILE))).configure()
    getLogger(__name__).info("Serving the gateway on port %d.", config.rest.port)
    server = RestServerFactory(GatewayRestApp(config).build(), config.rest).create()
    AsyncRunnableRunnerFactory(server).create().execute()
