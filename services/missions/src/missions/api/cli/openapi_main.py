from __future__ import annotations

# Standard library imports
from logging import getLogger

# First-party imports
from missions.api.rest.missions_rest_app import MissionsRestApp
from missions.models.config.missions_config import MissionsConfig
from swarm_logging.configurators.logging_configurator import LoggingConfigurator
from swarm_logging.models.logging_config import LoggingConfig
from swarm_rest.api.cli.openapi_cli import OpenApiCli


def main() -> None:
    """Configure logging, then write the document, or check it with ``--check``.

    Raises:
        SystemExit: When the check finds the file missing or out of date, or the arguments are refused.
    """
    config = MissionsConfig.load(MissionsConfig.conf_folder() / MissionsConfig.APP_FILE)
    logger_path = MissionsConfig.conf_folder() / MissionsConfig.LOGGER_FILE
    LoggingConfigurator(LoggingConfig(path=str(logger_path))).configure()
    logger = getLogger(__name__)
    cli = OpenApiCli(MissionsRestApp(config).build, MissionsRestApp.output_path())
    code = cli.main()
    if code != 0:
        logger.error("The OpenAPI command ended with exit code %d.", code)
        raise SystemExit(code)
    logger.debug("The OpenAPI command ended with exit code %d.", code)
