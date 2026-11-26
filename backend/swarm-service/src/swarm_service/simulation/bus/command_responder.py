from __future__ import annotations

# Standard library imports
from logging import Logger, getLogger
from typing import Optional

# Third-party imports
from nats.aio.client import Client

# First-party imports
from swarm_lifecycle.runnables.async_runnable import AsyncRunnable
from swarm_models.commands.command import Command
from swarm_models.config.simulator.simulator_config import SimulatorConfig
from swarm_models.simulation.commands.command_reply import CommandReply
from swarm_nats.clients.nats_connector import NatsConnector
from swarm_service.shared.bus.factories.nats_responder_factory import NatsResponderFactory
from swarm_service.simulation.bus.command_endpoint import CommandEndpoint
from swarm_service.simulation.drones.drone_service import DroneService


class CommandResponder(AsyncRunnable):
    """Answers the Commands of the Operator's Missions on the bus with the simulated Drones, until it is cancelled.

    Attributes:
        config (SimulatorConfig): The configuration of the Simulator.
        service (DroneService): Carries out the commands on the simulated Drones.
        connector (NatsConnector): Opens the connection to NATS, with the simulated credentials.
        client (Optional[Client]): The connection, once ``initialize`` has opened it.
        logger (Logger): Logger instance.

    Notes:
        - **The credentials are checked before this runnable is built** (``SimulatorServer``), so nothing connects
          with credentials that are not simulated (BR-014).
        - It was the ``serve`` command of the Simulator's command line: the app now runs it beside the server of its
          application, in ``SimulatorServer``, and a failure of it stops the app with an error.
        - ``close`` closes the service, then the connection, and is safe after a failed ``initialize``.
    """

    def __init__(
        self,
        config: SimulatorConfig,
        service: DroneService,
        connector: NatsConnector,
        logger: Optional[Logger] = None,
    ) -> None:
        """Prepare the responder, not yet connected.

        Args:
            config (SimulatorConfig): The configuration of the Simulator.
            service (DroneService): Carries out the commands.
            connector (NatsConnector): Opens the connection to NATS.
            logger (Optional[Logger]): Logger instance.
        """
        super().__init__(config.responder.status_interval_s)
        self.logger = logger if logger else getLogger(__name__)
        self.config = config
        self.service = service
        self.connector = connector
        self.client: Optional[Client] = None

    ############################
    # Publicly Exposed Methods #
    ############################

    async def initialize(self) -> None:
        """Connect to NATS and open the Drone service."""
        self.client = await self.connector.connect()
        await self.service.open()
        self.logger.info("The command responder is connected.")

    async def run(self) -> None:
        """Answer the commands of the bus until the responder ends or is cancelled."""
        if self.client is None:
            self.logger.debug("Nothing to answer: the responder is not connected.")
            return
        endpoint = CommandEndpoint(self.service)
        responder = NatsResponderFactory[Command, CommandReply](
            self.client, self.config.responder, Command, endpoint.handle
        ).create()
        async for status in responder.execute():
            self.logger.debug("The NATS responder is %s.", status)

    async def close(self) -> None:
        """Close the Drone service and the connection. Safe after a failed or partial ``initialize``."""
        await self.service.close()
        if self.client is None:
            self.logger.debug("The command responder was not connected.")
            return
        client, self.client = self.client, None
        await self.connector.disconnect(client)
        self.logger.info("Closed the command responder.")
