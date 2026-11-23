from __future__ import annotations

# Standard library imports
import asyncio
from logging import Logger, getLogger
from time import monotonic
from typing import ClassVar, Optional

# Third-party imports
import uvicorn
from fastapi import FastAPI

# First-party imports
from swarm_lifecycle.runnables.async_runnable import AsyncRunnable
from swarm_rest.models.config.rest_config import RestConfig
from swarm_rest.models.rest.exceptions import SERestServerStartError


class RestServer(AsyncRunnable):
    """Serves a FastAPI application with uvicorn, as an async runnable that yields its status.

    Attributes:
        START_TIMEOUT_S (ClassVar[float]): Seconds to wait for the server to accept connections.
        START_POLL_S (ClassVar[float]): Seconds between two checks that the server has started.
        app (FastAPI): The application served.
        config (RestConfig): The settings of the server.
        server (Optional[uvicorn.Server]): The uvicorn server, once ``initialize`` has built it.
        serving (Optional[asyncio.Task[None]]): The task that runs the uvicorn server.

    Notes:
        - ``log_config`` is ``None`` so that uvicorn leaves the logging to ``swarm_logging``.
        - **The start is detected by polling ``uvicorn.Server.started``**, which uvicorn sets once the sockets are
          bound, and a serving task that ends first is a failed start.
        - The serving task is waited on with ``asyncio.wait``, so that cancelling ``run`` never cancels uvicorn in the
          middle of its shutdown: ``close`` asks it to exit instead.
    """

    START_TIMEOUT_S: ClassVar[float] = 10.0
    START_POLL_S: ClassVar[float] = 0.01

    def __init__(self, app: FastAPI, config: RestConfig, logger: Optional[Logger] = None) -> None:
        """Initialise the server.

        Args:
            app (FastAPI): The application to serve.
            config (RestConfig): The settings of the server.
            logger (Optional[Logger]): Logger to use. A logger named after the module is used when it is ``None``.
        """
        super().__init__(config.status_interval_s)
        self.logger = logger if logger else getLogger(__name__)
        self.app = app
        self.config = config
        self.server: Optional[uvicorn.Server] = None
        self.serving: Optional[asyncio.Task[None]] = None

    ############################
    # Internal Helpers Methods #
    ############################

    async def _serve(self, server: uvicorn.Server) -> None:
        """Run the uvicorn server, turning its exit on a failed start into a Swarm error.

        Args:
            server (uvicorn.Server): The server to run.

        Raises:
            SERestServerStartError: If uvicorn exits the process because it cannot bind its port.
        """
        try:
            await server.serve()
        except SystemExit as error:
            self.logger.error("The server of %s exited with code %s.", type(self).__name__, error.code)
            raise SERestServerStartError(
                f"The server cannot listen on {self.config.host}:{self.config.port}."
            ) from error

    ############################
    # Publicly Exposed Methods #
    ############################

    async def initialize(self) -> None:
        """Start uvicorn in a task and wait until it accepts connections.

        Raises:
            SERestServerStartError: If the server has not started within ``START_TIMEOUT_S``, or stopped first.
        """
        uvicorn_config = uvicorn.Config(self.app, host=self.config.host, port=self.config.port, log_config=None)
        self.server = uvicorn.Server(uvicorn_config)
        self.serving = asyncio.create_task(self._serve(self.server))
        deadline = monotonic() + self.START_TIMEOUT_S
        while not self.server.started:
            if self.serving.done():
                self.logger.error("The server of %s stopped before it started.", type(self).__name__)
                await self.serving
                raise SERestServerStartError("The server stopped before it started.")
            if monotonic() >= deadline:
                self.logger.error(
                    "The server of %s did not start in %.1f s.", type(self).__name__, self.START_TIMEOUT_S
                )
                raise SERestServerStartError(f"The server did not start within {self.START_TIMEOUT_S} seconds.")
            await asyncio.sleep(self.START_POLL_S)
        self.logger.info("Serving on %s:%d.", self.config.host, self.config.port)

    async def run(self) -> None:
        """Wait until the serving task ends.

        Raises:
            Exception: Whatever the serving task raised, unchanged.
        """
        if self.serving is None:
            self.logger.debug("Nothing to run: the server was not initialised.")
            return
        await asyncio.wait({self.serving})
        if self.serving.cancelled():
            self.logger.debug("The serving task was cancelled.")
            return
        error = self.serving.exception()
        if error is not None:
            self.logger.error("The serving task failed with %s.", type(error).__name__)
            raise error
        self.logger.debug("The serving task ended.")

    async def close(self) -> None:
        """Ask the server to exit and wait for it, whether or not ``initialize`` succeeded."""
        if self.server is None or self.serving is None:
            self.logger.debug("Nothing to close: the server was not initialised.")
            return
        self.server.should_exit = True
        await asyncio.wait({self.serving})
        if self.serving.cancelled():
            self.logger.debug("The serving task had been cancelled.")
        elif self.serving.exception() is not None:
            self.logger.warning("The serving task ended with an error.")
        else:
            self.logger.info("Closed the server.")
        self.server = None
        self.serving = None
