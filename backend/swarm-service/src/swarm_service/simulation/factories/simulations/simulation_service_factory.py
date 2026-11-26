from __future__ import annotations

# Standard library imports
from logging import Logger, getLogger
from typing import Optional

# First-party imports
from swarm_lifecycle.factories.factory import Factory
from swarm_models.config.simulator.simulator_config import SimulatorConfig
from swarm_service.simulation.simulations.simulation_service import SimulationService


class SimulationServiceFactory(Factory[SimulationService]):
    """Builds the service that starts the simulated flights of the Squad.

    Attributes:
        config (SimulatorConfig): The configuration of the Simulator.
        logger (Logger): Logger instance.
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

    def _build(self) -> SimulationService:
        """Build the service, with no flight yet.

        Returns:
            SimulationService: The new service.
        """
        self.logger.debug("Building the simulation service.")
        return SimulationService(self.config)
