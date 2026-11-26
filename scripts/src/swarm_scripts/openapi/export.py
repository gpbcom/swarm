from __future__ import annotations

# Standard library imports
import sys
from logging import getLogger
from pathlib import Path

# First-party imports
from gateway.api.rest.gateway_rest_app import GatewayRestApp
from gateway.models.config.gateway_config import GatewayConfig
from swarm_logging.configurators.logging_configurator import LoggingConfigurator
from swarm_logging.models.logging_config import LoggingConfig
from swarm_rest.api.cli.openapi_cli import OpenApiCli


def main() -> None:
    """Configure logging, then write or check the OpenAPI document.

    Raises:
        SystemExit: Always, with the exit code of the command.
    """
    config = GatewayConfig.load(GatewayConfig.conf_folder() / GatewayConfig.APP_FILE)
    LoggingConfigurator(LoggingConfig(path=str(GatewayConfig.conf_folder() / GatewayConfig.LOGGER_FILE))).configure()
    code = OpenApiCli(GatewayRestApp(config).build, Path(GatewayRestApp.OPENAPI_OUTPUT)).main(sys.argv[1:])
    getLogger(__name__).debug("The OpenAPI command ended with exit code %d.", code)
    raise SystemExit(code)
