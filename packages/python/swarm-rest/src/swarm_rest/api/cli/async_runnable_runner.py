from __future__ import annotations

# Standard library imports
import asyncio
from logging import Logger, getLogger
from typing import Optional

# First-party imports
from swarm_lifecycle.models.enums import RunnableStatus
from swarm_lifecycle.runnables.async_runnable import AsyncRunnable
from swarm_lifecycle.runnables.runnable import Runnable


class AsyncRunnableRunner(Runnable):
    """Runs an async runnable to its end from synchronous code, such as a console script.

    Attributes:
        runnable (AsyncRunnable): The runnable to run.
        last_status (RunnableStatus): The last status the runnable yielded.
    """

    def __init__(self, runnable: AsyncRunnable, logger: Optional[Logger] = None) -> None:
        """Initialise the runner.

        Args:
            runnable (AsyncRunnable): The runnable to run.
            logger (Optional[Logger]): Logger to use. A logger named after the module is used when it is ``None``.
        """
        super().__init__()
        self.logger = logger if logger else getLogger(__name__)
        self.runnable = runnable
        self.last_status = RunnableStatus.NOT_STARTED

    ############################
    # Internal Helpers Methods #
    ############################

    async def _consume(self) -> None:
        """Read every status of the runnable, keeping the last one."""
        async for status in self.runnable.execute():
            self.last_status = status
            self.logger.debug("The runnable is %s.", status)

    ############################
    # Publicly Exposed Methods #
    ############################

    def initialize(self) -> None:
        """Acquire nothing: the runnable initialises itself."""
        self.logger.debug("Nothing to initialise.")

    def run(self) -> None:
        """Run the runnable in a new event loop until it ends.

        Raises:
            Exception: Whatever the runnable raised, unchanged.
        """
        asyncio.run(self._consume())

    def close(self) -> None:
        """Release nothing: the runnable closes itself."""
        self.logger.debug("Nothing to close.")
