from __future__ import annotations

# Standard library imports
from logging import Logger, getLogger
from typing import Optional

# Third-party imports
from fastapi import FastAPI

# First-party imports
from swarm_models.config.simulator.simulator_config import SimulatorConfig
from swarm_service.simulation.factories.bus.command_responder_factory import CommandResponderFactory
from swarm_service.simulation.factories.server_factory import ServerFactory
from swarm_service.simulation.servers.simulator_server import SimulatorServer
from swarm_web.factories.rest_server_factory import RestServerFactory


class SimulatorServerFactory(ServerFactory[SimulatorServer]):
    """Builds the runnable of the simulator app: the Command responder of the bus and the server of the application.

    Attributes:
        config (SimulatorConfig): The configuration of the Simulator.
        app (FastAPI): The application of the simulator app, which serves ``POST /v1/simulations``.
        logger (Logger): Logger instance.

    Notes:
        - The ``rest`` section of the configuration gives the host, the port and the status interval of the server,
          and its status interval is the runnable's too, because the server is the app's main work.
    """

    def __init__(self, config: SimulatorConfig, app: FastAPI, logger: Optional[Logger] = None) -> None:
        """Prepare the factory.

        Args:
            config (SimulatorConfig): The configuration of the Simulator.
            app (FastAPI): The application of the simulator app.
            logger (Optional[Logger]): Logger instance.
        """
        super().__init__()
        self.logger = logger if logger else getLogger(__name__)
        self.config = config
        self.app = app

    ############################
    # Internal Helpers Methods #
    ############################

    def _build(self) -> SimulatorServer:
        """Build the runnable of the responder and the server.

        Returns:
            SimulatorServer: A new runnable, not started.
        """
        self.logger.debug("Building the simulator server on port %d.", self.config.rest.port)
        return SimulatorServer(
            self.config,
            CommandResponderFactory(self.config),
            RestServerFactory(self.app, self.config.rest),
            self.config.rest.status_interval_s,
        )
