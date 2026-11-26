from __future__ import annotations

# Standard library imports
import asyncio
from logging import Logger, getLogger
from typing import Optional, Set

# First-party imports
from swarm_lifecycle.runnables.async_runnable import AsyncRunnable
from swarm_models.config.simulator.simulator_config import SimulatorConfig
from swarm_models.simulation.credentials.exceptions import SESimulatedCredentialsUnreadableError
from swarm_service.simulation.credentials.simulated_credentials_guard import SimulatedCredentialsGuard
from swarm_service.simulation.factories.bus.command_responder_factory import CommandResponderFactory
from swarm_web.factories.rest_server_factory import RestServerFactory


class SimulatorServer(AsyncRunnable):
    """Runs the Command responder of the bus and the server of the simulator app together, until one of them ends.

    Attributes:
        config (SimulatorConfig): The configuration of the Simulator.
        responder_factory (CommandResponderFactory): Builds the responder that answers the Commands of the bus.
        server_factory (RestServerFactory): Builds the server of the application that serves ``POST /v1/simulations``.
        logger (Logger): Logger instance.

    Notes:
        - **Nothing starts without simulated credentials (BR-014)**: ``initialize`` checks them before the responder
          and the server are built, so a refusal ends the app before anything connects to NATS or serves.
        - **A failure of the responder or of the server stops the other and is raised again**, so that the app's
          process ends with an error and is restarted. A responder that cannot reach NATS is such a failure: the app
          never serves ``POST /v1/simulations`` without answering the Commands of the bus.
        - The server ends when the process is asked to stop: uvicorn handles ``SIGINT`` and ``SIGTERM``, as in every
          app of Swarm, and the responder is then cancelled. The responder only ends when it is closed, so its end
          stops the server too.
        - The flight that flies is stopped by the lifespan of the application (``SimulationLifespan``), during the
          graceful stop of the server.
        - It was the ``serve`` command of the Simulator's command line, with the server of the app beside it.
    """

    def __init__(
        self,
        config: SimulatorConfig,
        responder_factory: CommandResponderFactory,
        server_factory: RestServerFactory,
        status_interval_s: float,
        logger: Optional[Logger] = None,
    ) -> None:
        """Prepare the runnable.

        Args:
            config (SimulatorConfig): The configuration of the Simulator.
            responder_factory (CommandResponderFactory): Builds the Command responder.
            server_factory (RestServerFactory): Builds the server of the application.
            status_interval_s (float): Seconds between two statuses.
            logger (Optional[Logger]): Logger instance.
        """
        super().__init__(status_interval_s)
        self.logger = logger if logger else getLogger(__name__)
        self.config = config
        self.responder_factory = responder_factory
        self.server_factory = server_factory

    ############################
    # Internal Helpers Methods #
    ############################

    async def _respond(self) -> None:
        """Run the Command responder until it ends."""
        async for status in self.responder_factory.create().execute():
            self.logger.debug("The command responder is %s.", status)
        self.logger.info("The command responder has ended.")

    async def _serve(self) -> None:
        """Run the server of the application until it ends."""
        async for status in self.server_factory.create().execute():
            self.logger.debug("The simulator server is %s.", status)
        self.logger.info("The simulator server has ended.")

    async def _stop(self, tasks: Set[asyncio.Task[None]]) -> None:
        """Cancel the tasks still running and wait for them.

        Args:
            tasks (Set[asyncio.Task[None]]): The tasks to stop.
        """
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        self.logger.debug("Stopped %d tasks.", len(tasks))

    ############################
    # Publicly Exposed Methods #
    ############################

    async def initialize(self) -> None:
        """Check that the NATS credentials of the configuration are simulated, before anything connects or serves.

        Raises:
            SESimulatedCredentialsUnreadableError: When no credentials file is configured, or it cannot be read.
            SESimulatedCredentialsNotSimulatedError: When the credentials are not tagged as simulated.
        """
        path = self.config.nats.credentials_path
        if path is None:
            self.logger.error("The Simulator has no credentials file.")
            raise SESimulatedCredentialsUnreadableError("No credentials file is configured.")
        SimulatedCredentialsGuard().check(path)
        self.logger.debug("The credentials are simulated.")

    async def run(self) -> None:
        """Run the responder and the server together until one of them ends or fails.

        Raises:
            Exception: Whatever the responder or the server raised, once the other is stopped.
        """
        pending: Set[asyncio.Task[None]] = {asyncio.create_task(self._respond()), asyncio.create_task(self._serve())}
        failure: Optional[BaseException] = None
        try:
            done, pending = await asyncio.wait(pending, return_when=asyncio.FIRST_COMPLETED)
        except asyncio.CancelledError:
            self.logger.debug("The simulator server is cancelled.")
            raise
        finally:
            await self._stop(pending)
        for task in done:
            if task.exception() is not None:
                failure = task.exception()
                self.logger.error("The simulator app failed: %s.", type(failure).__name__)
            else:
                self.logger.debug("A task of the simulator app has ended.")
        if failure is not None:
            self.logger.error("Stopped the simulator app after %s.", type(failure).__name__)
            raise failure
        self.logger.info("The simulator app has stopped.")

    async def close(self) -> None:
        """Release nothing: the responder and the server close themselves."""
        self.logger.debug("Nothing to release after the responder and the server.")
