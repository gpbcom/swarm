from __future__ import annotations

# Standard library imports
from logging import Logger, getLogger
from typing import Optional

# First-party imports
from swarm_models.config.simulator.simulator_config import SimulatorConfig
from swarm_nats.clients.nats_connector import NatsConnector
from swarm_service.shared.bus.factories.bus_runnable_factory import BusRunnableFactory
from swarm_service.simulation.bus.command_responder import CommandResponder
from swarm_service.simulation.factories.drones.drone_service_factory import DroneServiceFactory


class CommandResponderFactory(BusRunnableFactory[CommandResponder]):
    """Builds the responder that answers the Commands of the bus with the simulated Drones.

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

    def _build(self) -> CommandResponder:
        """Build one responder, with its own Drone service and connector.

        Returns:
            CommandResponder: A new responder, not connected yet.
        """
        self.logger.debug("Building the command responder on %s.", self.config.responder.subject)
        return CommandResponder(self.config, DroneServiceFactory(self.config).create(), NatsConnector(self.config.nats))
