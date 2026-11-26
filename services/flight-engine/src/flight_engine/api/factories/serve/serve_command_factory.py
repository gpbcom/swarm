from __future__ import annotations

# Standard library imports
from logging import Logger, getLogger
from pathlib import Path
from typing import Optional

# First-party imports
from flight_engine.api.cli.commands.command import Command
from flight_engine.api.cli.commands.serve_command import ServeCommand
from flight_engine.api.factories.command_factory import CommandFactory


class ServeCommandFactory(CommandFactory):
    """Factory of the command that serves the flight engine.

    Attributes:
        config_path (Path): The configuration file of the service.
        logger (Logger): Logger instance.
    """

    def __init__(self, config_path: Path, logger: Optional[Logger] = None) -> None:
        """Prepare the factory.

        Args:
            config_path (Path): The configuration file of the service.
            logger (Optional[Logger]): Logger instance.
        """
        super().__init__()
        self.logger = logger if logger else getLogger(__name__)
        self.config_path = config_path

    ############################
    # Internal Helpers Methods #
    ############################

    def _build(self) -> Command:
        """Build one serve command.

        Returns:
            Command: A new ``ServeCommand``.
        """
        self.logger.debug("Building a serve command for %s.", self.config_path)
        return ServeCommand(self.config_path)
