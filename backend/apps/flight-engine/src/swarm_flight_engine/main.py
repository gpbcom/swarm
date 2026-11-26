from __future__ import annotations

# Standard library imports
from logging import getLogger
from pathlib import Path

# First-party imports
from flight_engine.api.cli.cli_options import CliOptions
from flight_engine.api.cli.conf_locator import ConfLocator
from flight_engine.api.factories.serve.serve_command_factory import ServeCommandFactory
from swarm_logging.configurators.logging_configurator import LoggingConfigurator
from swarm_logging.models.logging_config import LoggingConfig


def main() -> None:
    """Read the options, configure logging once, then serve the flight engine until it is stopped.

    Raises:
        SystemExit: When the command exit code is not 0.

    Notes:
        - Logging is configured once, here at the entry point.
        - The command line holds ``--config``, whose default is ``conf/app.yaml``.
    """
    config_path = CliOptions().config_path()
    logger_path = ConfLocator().locate(Path(CliOptions.LOGGER_FILE))
    LoggingConfigurator(LoggingConfig(path=str(logger_path))).configure()
    command = ServeCommandFactory(config_path).create()
    command.execute()
    if command.exit_code != 0:
        getLogger(__name__).error("The flight engine ended with exit code %d.", command.exit_code)
        raise SystemExit(command.exit_code)
