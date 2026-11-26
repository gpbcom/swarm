from __future__ import annotations

# Standard library imports
import asyncio
from logging import Logger, getLogger
from typing import Optional, Set

# First-party imports
from swarm_lifecycle.runnables.async_runnable import AsyncRunnable
from swarm_service.flight.factories.engine.flight_engine_factory import FlightEngineFactory
from swarm_web.factories.rest_server_factory import RestServerFactory


class FlightEngineServer(AsyncRunnable):
    """Runs the flight engine of an edge and the server of its live socket together, until one fails or both end.

    Attributes:
        engine_factory (FlightEngineFactory): Builds the flight engine.
        server_factory (RestServerFactory): Builds the server of the application that serves the live socket.
        logger (Logger): Logger instance.

    Notes:
        - One asyncio process, with one ``LiveHub`` and one ``LiveCodec`` shared by the Mission actors and the sockets:
          the app wires them into both factories.
        - The engine may end by itself, for example with no Mission to fly: the server keeps serving.
        - **A failure of the engine or of the server stops the other and is raised again**, so that the app's process
          ends with an error and is restarted.
        - The server ends when the process is asked to stop: uvicorn handles ``SIGINT`` and ``SIGTERM``, as in every
          app of Swarm, and the engine is then cancelled.
        - It was the ``serve`` command of the flight engine's command line.
    """

    def __init__(
        self,
        engine_factory: FlightEngineFactory,
        server_factory: RestServerFactory,
        status_interval_s: float,
        logger: Optional[Logger] = None,
    ) -> None:
        """Prepare the runnable.

        Args:
            engine_factory (FlightEngineFactory): Builds the flight engine.
            server_factory (RestServerFactory): Builds the server of the live socket.
            status_interval_s (float): Seconds between two statuses.
            logger (Optional[Logger]): Logger instance.
        """
        super().__init__(status_interval_s)
        self.logger = logger if logger else getLogger(__name__)
        self.engine_factory = engine_factory
        self.server_factory = server_factory

    ############################
    # Internal Helpers Methods #
    ############################

    async def _fly(self) -> None:
        """Run the flight engine until it ends."""
        async for status in self.engine_factory.create().execute():
            self.logger.debug("The flight engine is %s.", status)
        self.logger.info("The flight engine has ended.")

    async def _serve(self) -> None:
        """Run the server of the live socket until it ends."""
        async for status in self.server_factory.create().execute():
            self.logger.debug("The live server is %s.", status)
        self.logger.info("The live server has ended.")

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
        """Acquire nothing: the engine and the server initialise themselves when they run."""
        self.logger.debug("Nothing to initialise before the engine and the server run.")

    async def run(self) -> None:
        """Run the engine and the server together until the server ends or one of them fails.

        Raises:
            Exception: Whatever the engine or the server raised, once the other is stopped.
        """
        engine = asyncio.create_task(self._fly())
        server = asyncio.create_task(self._serve())
        pending: Set[asyncio.Task[None]] = {engine, server}
        failure: Optional[BaseException] = None
        try:
            while server in pending and failure is None:
                done, pending = await asyncio.wait(pending, return_when=asyncio.FIRST_COMPLETED)
                for task in done:
                    if task.exception() is not None:
                        failure = task.exception()
                        self.logger.error("The flight engine app failed: %s.", type(failure).__name__)
                    else:
                        self.logger.debug("A task of the flight engine app has ended.")
        finally:
            await self._stop(pending)
        if failure is not None:
            self.logger.error("Stopped the flight engine app after %s.", type(failure).__name__)
            raise failure

    async def close(self) -> None:
        """Release nothing: the engine and the server close themselves."""
        self.logger.debug("Nothing to release after the engine and the server.")
