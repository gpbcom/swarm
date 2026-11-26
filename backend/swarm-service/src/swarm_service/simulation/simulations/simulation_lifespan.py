from __future__ import annotations

# Standard library imports
import asyncio
from contextlib import asynccontextmanager
from logging import Logger, getLogger
from typing import AsyncIterator, Optional

# Third-party imports
from fastapi import FastAPI

# First-party imports
from swarm_models.config.simulator.simulator_config import SimulatorConfig
from swarm_models.simulation.credentials.exceptions import SESimulatedCredentialsUnreadableError
from swarm_service.simulation.credentials.simulated_credentials_guard import SimulatedCredentialsGuard
from swarm_service.simulation.factories.bus.command_responder_factory import CommandResponderFactory
from swarm_service.simulation.simulations.simulation_service import SimulationService


class SimulationLifespan:
    """Runs the background work of the simulator app for as long as its application lives.

    Attributes:
        config (SimulatorConfig): The configuration of the Simulator.
        simulations (SimulationService): The service of ``POST /v1/simulations``, whose flight is stopped with the app.
        task (Optional[asyncio.Task[None]]): The task that reads the statuses of the command responder.
        logger (Logger): Logger instance.

    Notes:
        - **Nothing starts without simulated credentials (BR-014)**: the credentials are checked before the
          responder is built, and a refusal fails the start of the application, so the app never serves and never
          connects to NATS. It is the refusal the ``serve`` command made.
        - Answering the Commands of the bus is the app's normal background work: the responder is consumed through
          ``execute()``, so its status is read and logged, and ``close`` runs when the task ends.
        - **A responder that fails, such as on a NATS server that cannot be reached, is logged at ``ERROR`` and the
          application keeps serving** ``POST /v1/simulations``, as the gateway does with its live feed.
        - When the application stops, the responder is cancelled and the flight that flies is stopped.
    """

    def __init__(
        self, config: SimulatorConfig, simulations: SimulationService, logger: Optional[Logger] = None
    ) -> None:
        """Initialise the lifespan.

        Args:
            config (SimulatorConfig): The configuration of the Simulator.
            simulations (SimulationService): The service whose flight is stopped with the application.
            logger (Optional[Logger]): Logger instance.
        """
        self.logger = logger if logger else getLogger(__name__)
        self.config = config
        self.simulations = simulations
        self.task: Optional[asyncio.Task[None]] = None

    ############################
    # Internal Helpers Methods #
    ############################

    def _check_credentials(self) -> None:
        """Check that the NATS credentials of the configuration are simulated.

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

    async def _respond(self) -> None:
        """Read the statuses of the command responder until it ends."""
        try:
            async for status in CommandResponderFactory(self.config).create().execute():
                self.logger.debug("The command responder is %s.", status)
        except Exception as error:  # noqa: BLE001
            self.logger.error("The command responder stopped: %s.", type(error).__name__)

    ############################
    # Publicly Exposed Methods #
    ############################

    @asynccontextmanager
    async def lifespan(self, app: FastAPI) -> AsyncIterator[None]:
        """Check the credentials, answer the Commands of the bus while the application serves, then stop.

        Args:
            app (FastAPI): The application.

        Yields:
            None: While the application serves.

        Raises:
            SESimulatedCredentialsError: When the credentials are not simulated, before anything connects.
        """
        self._check_credentials()
        self.task = asyncio.create_task(self._respond())
        self.logger.info("The command responder is started.")
        try:
            yield
        except BaseException:
            self.logger.error("The application stopped with an error.")
            raise
        finally:
            task, self.task = self.task, None
            if task is not None:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    self.logger.debug("The command responder task is cancelled.")
            else:
                self.logger.debug("No command responder task to cancel.")
            await self.simulations.close()
            self.logger.info("The command responder and the flight are stopped.")
