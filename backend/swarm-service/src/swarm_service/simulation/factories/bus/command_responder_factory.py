from __future__ import annotations

# Standard library imports
from logging import Logger, getLogger
from typing import Optional

# First-party imports
from simulator.api.cli.commands.serve_command import ServeCommand
from simulator.api.factories.command_factory import CommandFactory
from simulator.models.config.simulator_config import SimulatorConfig


class ServeCommandFactory(CommandFactory):
    """Builds the command that serves the commands of a Mission.

    Attributes:
        config (SimulatorConfig): The configuration of the Simulator.
    """

    def __init__(self, config: SimulatorConfig, logger: Optional[Logger] = None) -> None:
        """Prepare the factory.

        Args:
            config (SimulatorConfig): The configuration of the Simulator.
            logger (Optional[Logger]): Logger instance.
        """
        super().__init__()
        self.logger = logger if logger else getLogger(__name__)
        self.config = config

    ############################
    # Internal Helpers Methods #
    ############################

    def _build(self) -> ServeCommand:
        """Build one serve command.

        Returns:
            ServeCommand: A new command, not run.
        """
        self.logger.debug("Building a serve command.")
        return ServeCommand(self.config)
