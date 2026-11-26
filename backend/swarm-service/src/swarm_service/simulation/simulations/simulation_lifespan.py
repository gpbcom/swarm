from __future__ import annotations

# Standard library imports
from contextlib import asynccontextmanager
from logging import Logger, getLogger
from typing import AsyncIterator, Optional

# Third-party imports
from fastapi import FastAPI

# First-party imports
from swarm_service.simulation.simulations.simulation_service import SimulationService


class SimulationLifespan:
    """Stops the flight of the simulator app when its application stops.

    Attributes:
        simulations (SimulationService): The service of ``POST /v1/simulations``, whose flight is stopped with the app.
        logger (Logger): Logger instance.

    Notes:
        - **The flight is stopped during the graceful stop of the server**, so that it is closed cleanly before
          uvicorn raises the stop signal it caught again, which ends the process at once.
        - The simulated credentials (BR-014) and the Command responder are the job of ``SimulatorServer``, which
          checks the credentials before the server starts and stops the app when the responder fails.
    """

    def __init__(self, simulations: SimulationService, logger: Optional[Logger] = None) -> None:
        """Initialise the lifespan.

        Args:
            simulations (SimulationService): The service whose flight is stopped with the application.
            logger (Optional[Logger]): Logger instance.
        """
        self.logger = logger if logger else getLogger(__name__)
        self.simulations = simulations

    ############################
    # Publicly Exposed Methods #
    ############################

    @asynccontextmanager
    async def lifespan(self, app: FastAPI) -> AsyncIterator[None]:
        """Let the application serve, then stop the flight that flies.

        Args:
            app (FastAPI): The application.

        Yields:
            None: While the application serves.
        """
        self.logger.debug("The simulator application serves.")
        try:
            yield
        except BaseException as error:
            self.logger.error("The application stopped with %s.", type(error).__name__)
            raise
        finally:
            await self.simulations.close()
            self.logger.info("The flight of the simulator application is stopped.")
