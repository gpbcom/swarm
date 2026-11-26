from __future__ import annotations

# Standard library imports
import asyncio
from abc import ABC, abstractmethod
from logging import Logger, getLogger
from time import monotonic
from typing import AsyncIterator, Optional

# First-party imports
from swarm_lifecycle.models.enums import RunnableStatus
from swarm_lifecycle.models.exceptions import SEAsyncRunnableInvalidStatusIntervalError


class AsyncRunnable(ABC):
    """Base class of everything that is initialised, run and closed in an event loop.

    Attributes:
        status_interval_s (float): Seconds between two statuses while the runnable works.
        status (RunnableStatus): What the runnable is doing now.
        logger (Logger): Logger instance.

    Notes:
        - ``Runnable`` is a separate class and shares no base with this one, because the methods of one are plain
          methods and those of the other are coroutines, and no single signature fits both.
        - **``close`` must be safe after a failed or partial ``initialize``**, because ``execute`` always calls it.
        - **A long-running async task always yields its status** (AGENT.md, Lifecycle and factories): ``execute`` is an
          async generator of ``RunnableStatus``. It yields the status every ``status_interval_s`` while the work goes
          on, and ``EXECUTED`` when it succeeds, so a caller always knows what the task is doing. The interval comes
          from the runnable's configuration, so the base sets no default.
    """

    def __init__(self, status_interval_s: float, logger: Optional[Logger] = None) -> None:
        """Initialise the runnable.

        Args:
            status_interval_s (float): Seconds between two statuses, from the runnable's configuration.
            logger (Optional[Logger]): Logger to use. A logger named after the module is used when it is ``None``.

        Raises:
            SEAsyncRunnableInvalidStatusIntervalError: If ``status_interval_s`` is not a positive number.
        """
        self.logger = logger if logger else getLogger(__name__)
        if (
            isinstance(status_interval_s, bool)
            or not isinstance(status_interval_s, (int, float))
            or status_interval_s <= 0
        ):
            self.logger.error("Refused the status interval of %s.", type(self).__name__)
            raise SEAsyncRunnableInvalidStatusIntervalError(
                f"Invalid status_interval_s: {status_interval_s!r}. Must be a number of seconds greater than 0."
            )
        self.status_interval_s = float(status_interval_s)
        self.status = RunnableStatus.NOT_STARTED

    ############################
    # Internal Helpers Methods #
    ############################

    async def _initialize_and_run(self) -> None:
        """Call ``initialize`` then ``run``, keeping ``status`` up to date."""
        self.status = RunnableStatus.INITIALISING
        await self.initialize()
        self.status = RunnableStatus.RUNNING
        await self.run()

    async def _cancel(self, work: asyncio.Task[None], name: str) -> None:
        """Cancel the work if it is still going on, for example when the caller stopped reading the statuses.

        Args:
            work (asyncio.Task[None]): The task running ``_initialize_and_run``.
            name (str): The class name of the runnable, for the log lines.
        """
        if work.done():
            self.logger.debug("Nothing to cancel: the work of %s has ended.", name)
            return
        work.cancel()
        try:
            await work
        except asyncio.CancelledError:
            self.logger.warning("Cancelled %s while %s.", name, self.status)

    ############################
    # Publicly Exposed Methods #
    ############################

    @abstractmethod
    async def initialize(self) -> None:
        """Acquire what the work needs. A service is already serving when this returns."""

    @abstractmethod
    async def run(self) -> None:
        """Do the work. A service blocks here until it is closed, and a job returns when it is done."""

    @abstractmethod
    async def close(self) -> None:
        """Release everything. It must be safe after a failed or partial ``initialize``."""

    async def execute(self) -> AsyncIterator[RunnableStatus]:
        """Call ``initialize``, ``run`` and ``close``, yield the status while working, and close whatever happens.

        Read it with ``async for status in runnable.execute()``.

        Yields:
            RunnableStatus: ``INITIALISING`` or ``RUNNING`` every ``status_interval_s`` while the work goes on, then
            ``EXECUTED`` when the work succeeded. Each one is also logged at ``INFO`` with the time elapsed.

        Raises:
            Exception: Whatever ``initialize``, ``run`` or ``close`` raised, unchanged.

        Notes:
            - The broad ``except`` only logs the failure at ``ERROR`` and raises it again unchanged: ``execute`` must
              report any failure of the work, whatever its type, without swallowing it.
            - **When the caller stops reading the statuses, the work is cancelled and ``close`` still runs.**
        """
        name = type(self).__name__
        started = monotonic()
        self.logger.debug("Executing %s, with a status every %s s.", name, self.status_interval_s)
        work = asyncio.create_task(self._initialize_and_run())
        try:
            while not work.done():
                await asyncio.wait({work}, timeout=self.status_interval_s)
                if not work.done():
                    self.logger.info("Status of %s: %s after %.1f s.", name, self.status, monotonic() - started)
                    yield self.status
            await work
        except Exception as error:
            duration_ms = int((monotonic() - started) * 1000)
            self.logger.error("Execution of %s stopped by %s after %d ms.", name, type(error).__name__, duration_ms)
            raise
        finally:
            await self._cancel(work, name)
            await self.close()
        self.status = RunnableStatus.EXECUTED
        self.logger.info("Executed %s in %d ms.", name, int((monotonic() - started) * 1000))
        yield self.status
