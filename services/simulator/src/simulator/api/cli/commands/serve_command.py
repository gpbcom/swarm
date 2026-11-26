from __future__ import annotations

# Standard library imports
import asyncio
import signal
from logging import Logger, getLogger
from typing import ClassVar, Optional, Tuple

# Third-party imports
from nats.aio.client import Client

# First-party imports
from simulator.api.bus.command_endpoint import CommandEndpoint
from simulator.api.cli.commands.command import Command
from simulator.models.commands.command_reply import CommandReply
from simulator.models.config.simulator_config import SimulatorConfig
from simulator.models.credentials.exceptions import SESimulatedCredentialsError
from simulator.service.commands.simulated_command_service import SimulatedCommandService
from simulator.service.credentials.simulated_credentials_guard import SimulatedCredentialsGuard
from simulator.service.factories.commands.simulated_command_service_factory import SimulatedCommandServiceFactory
from swarm_models.commands.command import Command as BusCommand
from swarm_nats.api.bus.nats_responder import NatsResponder
from swarm_nats.api.factories.bus.nats_responder_factory import NatsResponderFactory
from swarm_nats.clients.nats_connector import NatsConnector
from swarm_nats.models.bus.exceptions import SENatsConnectionError


class ServeCommand(Command):
    """Command that answers the commands of a Mission on the bus until it is stopped.

    Attributes:
        EXIT_FAILED (int): The exit code when the connection to NATS cannot be opened.
        EXIT_REFUSED_CREDENTIALS (int): The exit code when the credentials are not simulated or not readable.
        STOP_SIGNALS (Tuple[signal.Signals, ...]): The signals that stop the service.
        REFUSED_LINE (str): The line printed when the credentials are refused.
        FAILED_LINE (str): The line printed when the connection fails.
        config (SimulatorConfig): The configuration of the Simulator.
        exit_code (int): ``0`` after a clean stop, ``3`` when the credentials were refused, ``1`` on a connection failure.
        logger (Logger): Logger instance.

    Notes:
        - **The credentials are checked first and nothing connects when they are refused (BR-014).**
        - ``SIGTERM`` and ``SIGINT`` end the service cleanly: the responder, the service and the connection are closed.
        - Only ``api/cli/`` prints, because this output is for the person at the terminal.
    """

    EXIT_FAILED: ClassVar[int] = 1
    EXIT_REFUSED_CREDENTIALS: ClassVar[int] = 3
    STOP_SIGNALS: ClassVar[Tuple[signal.Signals, ...]] = (signal.SIGTERM, signal.SIGINT)
    REFUSED_LINE: ClassVar[str] = "Refused the credentials: {reason}"
    FAILED_LINE: ClassVar[str] = "Could not connect to NATS: {reason}"

    def __init__(self, config: SimulatorConfig, logger: Optional[Logger] = None) -> None:
        """Prepare the command.

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

    def _refuse(self, reason: str) -> None:
        """Record a refusal of the credentials.

        Args:
            reason (str): Why they are refused.
        """
        self.logger.error("The Simulator refused its credentials.")
        self.exit_code = self.EXIT_REFUSED_CREDENTIALS
        print(self.REFUSED_LINE.format(reason=reason))

    async def _consume(self, responder: NatsResponder[BusCommand, CommandReply]) -> None:
        """Read the statuses of the responder until it ends.

        Args:
            responder (NatsResponder[BusCommand, CommandReply]): The responder.
        """
        async for status in responder.execute():
            self.logger.debug("The responder is %s.", status)

    async def _respond(self, client: Client, service: SimulatedCommandService) -> None:
        """Answer the commands of the bus until ``SIGTERM`` or ``SIGINT``.

        Args:
            client (Client): The connected NATS client.
            service (SimulatedCommandService): The open service.
        """
        endpoint = CommandEndpoint(service)
        responder = NatsResponderFactory[BusCommand, CommandReply](
            client, self.config.responder, BusCommand, endpoint.handle
        ).create()
        stop = asyncio.Event()
        loop = asyncio.get_running_loop()
        for stop_signal in self.STOP_SIGNALS:
            loop.add_signal_handler(stop_signal, stop.set)
        consumer = asyncio.create_task(self._consume(responder))
        stopper = asyncio.create_task(stop.wait())
        await asyncio.wait({consumer, stopper}, return_when=asyncio.FIRST_COMPLETED)
        stopper.cancel()
        for stop_signal in self.STOP_SIGNALS:
            loop.remove_signal_handler(stop_signal)
        if consumer.done():
            self.logger.warning("The responder ended before any stop signal.")
            await consumer
            return
        self.logger.info("Stop signal received, closing the responder.")
        consumer.cancel()
        try:
            await consumer
        except asyncio.CancelledError:
            self.logger.debug("The responder was cancelled and closed.")

    async def _serve(self) -> None:
        """Connect to NATS, open the service and answer commands, then close everything."""
        service = SimulatedCommandServiceFactory(self.config).create()
        connector = NatsConnector(self.config.nats)
        try:
            client = await connector.connect()
        except SENatsConnectionError as error:
            self.exit_code = self.EXIT_FAILED
            print(self.FAILED_LINE.format(reason=type(error).__name__))
            return
        try:
            await service.open()
            await self._respond(client, service)
        except Exception as error:
            self.logger.error("Serving stopped by %s.", type(error).__name__)
            raise
        finally:
            await service.close()
            await connector.disconnect(client)

    ############################
    # Publicly Exposed Methods #
    ############################

    def initialize(self) -> None:
        """Check that the credentials are simulated, before anything connects."""
        path = self.config.nats.credentials_path
        if path is None:
            self._refuse("no credentials file.")
            return
        try:
            SimulatedCredentialsGuard().check(path)
        except SESimulatedCredentialsError as error:
            self._refuse(str(error))
            return
        self.logger.debug("The credentials are simulated.")

    def run(self) -> None:
        """Serve the commands of the Mission until a stop signal, unless the credentials were refused."""
        if self.exit_code != 0:
            self.logger.debug("Not serving: the credentials were refused.")
            return
        asyncio.run(self._serve())

    def close(self) -> None:
        """Release nothing: ``run`` closes the responder, the service and the connection itself."""
        self.logger.debug("Nothing to release after serving.")
