from __future__ import annotations

# Standard library imports
import asyncio
from contextlib import asynccontextmanager
from logging import Logger, getLogger
from typing import AsyncIterator, Optional

# Third-party imports
from fastapi import FastAPI

# First-party imports
from gateway.service.live.live_feed import LiveFeed


class LiveFeedLifespan:
    """Runs the live feed of the gateway for as long as its application lives.

    Attributes:
        feed (LiveFeed): The live feed to run.
        task (Optional[asyncio.Task[None]]): The task that reads the statuses of the feed, while the app lives.
        logger (Logger): Logger instance.

    Notes:
        - The feed is consumed through ``execute()``, so its status is read and logged, and ``close`` runs when the
          task ends.
        - **A feed that fails is logged and the application keeps serving**: a client then gets no live source and its
          socket is closed.
    """

    def __init__(self, feed: LiveFeed, logger: Optional[Logger] = None) -> None:
        """Initialise the lifespan.

        Args:
            feed (LiveFeed): The live feed to run.
            logger (Optional[Logger]): Logger instance.
        """
        self.logger = logger if logger else getLogger(__name__)
        self.feed = feed
        self.task: Optional[asyncio.Task[None]] = None

    ############################
    # Internal Helpers Methods #
    ############################

    async def _consume(self) -> None:
        """Read the statuses of the feed until it ends."""
        try:
            async for status in self.feed.execute():
                self.logger.debug("The live feed is %s.", status)
        except Exception as error:  # noqa: BLE001
            self.logger.error("The live feed stopped: %s.", type(error).__name__)

    ############################
    # Publicly Exposed Methods #
    ############################

    @asynccontextmanager
    async def lifespan(self, app: FastAPI) -> AsyncIterator[None]:
        """Start the feed with the application and stop it with it.

        Args:
            app (FastAPI): The application.

        Yields:
            None: While the application serves.
        """
        self.task = asyncio.create_task(self._consume())
        self.logger.info("The live feed is started.")
        try:
            yield
        except BaseException:
            self.logger.error("The application stopped with an error.")
            raise
        finally:
            task = self.task
            self.task = None
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                self.logger.debug("The live feed task is cancelled.")
            self.logger.info("The live feed is stopped.")
