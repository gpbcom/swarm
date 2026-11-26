from __future__ import annotations

# Standard library imports
from logging import Logger, getLogger
from typing import Optional
from uuid import UUID

# First-party imports
from simulator.api.cli.commands.fly_command import FlyCommand
from simulator.api.factories.command_factory import CommandFactory
from simulator.models.config.simulator_config import SimulatorConfig


class FlyCommandFactory(CommandFactory):
    """Builds the command that flies the simulated Squad once.

    Attributes:
        config (SimulatorConfig): The configuration of the Simulator.
        mission_id (UUID): The Mission the Flight log belongs to.
    """

    def __init__(self, config: SimulatorConfig, mission_id: UUID, logger: Optional[Logger] = None) -> None:
        """Prepare the factory.

        Args:
            config (SimulatorConfig): The configuration of the Simulator.
            mission_id (UUID): The Mission the Flight log belongs to.
            logger (Optional[Logger]): Logger instance.
        """
        super().__init__()
        self.logger = logger if logger else getLogger(__name__)
        self.config = config
        self.mission_id = mission_id

    ############################
    # Internal Helpers Methods #
    ############################

    def _build(self) -> FlyCommand:
        """Build one fly command.

        Returns:
            FlyCommand: A new command, not run.
        """
        self.logger.debug("Building a fly command for Mission %s.", self.mission_id)
        return FlyCommand(self.config, self.mission_id)
