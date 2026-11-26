from __future__ import annotations

# Standard library imports
from logging import getLogger
from pathlib import Path

# First-party imports
from fleet.api.rest.fleet_rest_app import FleetRestApp
from fleet.models.config.fleet_config import FleetConfig
from swarm_logging.configurators.logging_configurator import LoggingConfigurator
from swarm_logging.models.logging_config import LoggingConfig
from swarm_rest.api.cli.openapi_cli import OpenApiCli


def main() -> None:
    """Configure logging once, then write or check the OpenAPI document.

    Raises:
        SystemExit: When the exit code is not 0.

    Notes:
        - Logging is configured once, here at the entry point.
        - The default file is ``FleetRestApp.OPENAPI_OUTPUT`` under the repository root.
    """
    folder = FleetConfig.conf_folder()
    config = FleetConfig.load(folder / FleetConfig.APP_FILE)
    LoggingConfigurator(LoggingConfig(path=str(folder / FleetConfig.LOGGER_FILE))).configure()
    root = Path(__file__).resolve().parents[6]
    code = OpenApiCli(FleetRestApp(config).build, root / FleetRestApp.OPENAPI_OUTPUT).main()
    if code != 0:
        getLogger(__name__).error("The OpenAPI command ended with exit code %d.", code)
        raise SystemExit(code)
