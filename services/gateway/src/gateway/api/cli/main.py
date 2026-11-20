from __future__ import annotations

# Standard library imports
from logging import getLogger

# First-party imports
from gateway.api.factories.greeting.greeting_command_factory import GreetingCommandFactory
from swarm_logging.configurators.logging_configurator import LoggingConfigurator
from swarm_logging.models.logging_config import LoggingConfig


def main() -> None:
    """Configure logging, then run the greeting command.

    Raises:
        SystemExit: When the command exit code is not 0.

    Notes:
        - Logging is configured once, here at the entry point.
        - Only ``api/cli/`` prints, because this output is for the person at the terminal.
    """
    LoggingConfigurator(LoggingConfig()).configure()
    command = GreetingCommandFactory().create()
    command.execute()
    if command.exit_code != 0:
        getLogger(__name__).error("The greeting command ended with exit code %d.", command.exit_code)
        raise SystemExit(command.exit_code)
