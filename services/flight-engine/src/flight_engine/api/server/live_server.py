from __future__ import annotations

# Standard library imports
import asyncio
from contextlib import nullcontext
from logging import Logger, getLogger
from typing import ClassVar, Optional

# Third-party imports
import uvicorn
from fastapi import FastAPI

# First-party imports
from flight_engine.models.config.live_server_config import LiveServerConfig
from swarm_lifecycle.runnables.async_runnable import AsyncRunnable


class LiveServer(AsyncRunnable):
    """Serves the local live application of the flight engine with uvicorn.

    Attributes:
        STARTUP_POLL_S (ClassVar[float]): How often ``initialize`` checks that the server has started.
        CAPTURE_SIGNALS (ClassVar[str]): The name of the uvicorn method that installs its signal handlers.
        app (FastAPI): The application to serve.
        config (LiveServerConfig): The host, the port and the status interval.
        server (Optional[uvicorn.Server]): The uvicorn server, once ``initialize`` has built it.
        task (Optional[asyncio.Task[None]]): The task running the server.
        logger (Logger): Logger instance.

    Notes:
        - It serves once ``initialize`` returns, and ``close`` asks uvicorn to exit and waits for it.
        - **uvicorn's own signal handlers are switched off**, because the command that runs the engine and the server
          together owns SIGINT and SIGTERM and stops both.
    """

    STARTUP_POLL_S: ClassVar[float] = 0.01
    CAPTURE_SIGNALS: ClassVar[str] = "capture_signals"

    def __init__(self, app: FastAPI, config: LiveServerConfig, logger: Optional[Logger] = None) -> None:
        """Prepare the server, not yet listening.

        Args:
            app (FastAPI): The application to serve.
            config (LiveServerConfig): The host, the port and the status interval.
            logger (Optional[Logger]): Logger instance.
        """
        super().__init__(config.status_interval_s)
        self.logger = logger if logger else getLogger(__name__)
        self.app = app
        self.config = config
        self.server: Optional[uvicorn.Server] = None
        self.task: Optional[asyncio.Task[None]] = None

    ############################
    # Publicly Exposed Methods #
    ############################

    async def initialize(self) -> None:
        """Start uvicorn and wait until it listens.

        Raises:
            RuntimeError: If uvicorn stops before it listens, for instance when the port is taken.
        """
        settings = uvicorn.Config(self.app, host=self.config.host, port=self.config.port, log_config=None)
        server = uvicorn.Server(settings)
        setattr(server, self.CAPTURE_SIGNALS, nullcontext)
        self.server = server
        self.task = asyncio.create_task(server.serve())
        while not server.started:
            if self.task.done():
                self.logger.error("The live server stopped before it listened on port %d.", self.config.port)
                raise RuntimeError(f"The live server could not listen on {self.config.host}:{self.config.port}.")
            await asyncio.sleep(self.STARTUP_POLL_S)
        self.logger.info("Serving the live socket on %s:%d.", self.config.host, self.config.port)

    async def run(self) -> None:
        """Block until the server has stopped, without cancelling it when ``run`` is cancelled."""
        if self.task is None:
            self.logger.debug("The live server was not started.")
            return
        await asyncio.shield(self.task)

    async def close(self) -> None:
        """Ask uvicorn to exit and wait for it. Safe after a failed or partial ``initialize``."""
        if self.server is None or self.task is None:
            self.logger.debug("The live server was not started.")
            return
        server, task = self.server, self.task
        self.server, self.task = None, None
        server.should_exit = True
        try:
            await task
        except asyncio.CancelledError:
            self.logger.debug("The live server task was cancelled.")
        self.logger.info("Closed the live server.")
