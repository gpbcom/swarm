from __future__ import annotations

# Standard library imports
import asyncio
from abc import ABC, abstractmethod
from logging import Logger, getLogger
from time import monotonic
from typing import Optional

# First-party imports
from swarm_lifecycle.models.exceptions import SEAsyncRunnableInvalidStatusIntervalError


class AsyncRunnable(ABC):
    """Base class of everything that is initialised, run and closed in an event loop.

    Attributes:
        status_interval_s (float): Seconds between two status reports while the runnable works.
        logger (Logger): Logger instance.

    Notes:
        - ``Runnable`` is a separate class and shares no base with this one, because the methods of one are plain
          methods and those of the other are coroutines, and no single signature fits both.
        - **``close`` must be safe after a failed or partial ``initialize``**, because ``execute`` always calls it.
        - **A long-running async task always reports its status** (AGENT.md, Lifecycle and factories): while
          ``initialize`` and ``run`` work, ``execute`` logs ``status()`` at ``INFO`` every ``status_interval_s``, then
          a last status when the work stops. Every subclass therefore implements ``status``, and the interval comes
          from its configuration, so the base sets no default.
    """

    def __init__(self, status_interval_s: float, logger: Optional[Logger] = None) -> None:
        """Initialise the runnable.

        Args:
            status_interval_s (float): Seconds between two status reports, from the runnable's configuration.
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

    ############################
    # Internal Helpers Methods #
    ############################

    async def _report_status(self, name: str) -> None:
        """Log the status at ``INFO`` every ``status_interval_s``, until cancelled.

        Args:
            name (str): The class name of the runnable, for the log lines.
        """
        while True:
            await asyncio.sleep(self.status_interval_s)
            self.logger.info("Status of %s: %s", name, self.status())

    async def _stop_reporting(self, reporter: asyncio.Task[None], name: str) -> None:
        """Stop the periodic status reports, then log the last status.

        Args:
            reporter (asyncio.Task[None]): The task running ``_report_status``.
            name (str): The class name of the runnable, for the log lines.

        Notes:
            **The broad ``except`` is deliberate:** a failing ``status`` is a degraded report, logged at ``WARNING``.
            It must neither stop the work nor hide the error that ``execute`` is raising.
        """
        reporter.cancel()
        try:
            await reporter
        except asyncio.CancelledError:
            self.logger.debug("Stopped the status reports of %s.", name)
        except Exception as error:  # noqa: BLE001
            self.logger.warning("The status reports of %s failed with %s.", name, type(error).__name__)
        self.logger.info("Last status of %s: %s", name, self.status())

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

    @abstractmethod
    def status(self) -> str:
        """Return one line saying what the runnable is doing and how far it got.

        Returns:
            str: The status, for example ``Serving: 12 requests answered.``
        """

    async def execute(self) -> None:
        """Call ``initialize``, ``run`` and ``close``, report the status while working, and close whatever happens.

        Raises:
            Exception: Whatever ``initialize``, ``run`` or ``close`` raised, unchanged.

        Notes:
            - The broad ``except`` only logs the failure at ``ERROR`` and raises it again unchanged: ``execute`` must
              report any failure of the work, whatever its type, without swallowing it.
            - The status reports stop, and the last status is logged, before ``close``, so that they describe the work
              and not the release.
        """
        name = type(self).__name__
        started = monotonic()
        self.logger.debug("Executing %s, with a status every %s s.", name, self.status_interval_s)
        reporter = asyncio.create_task(self._report_status(name))
        try:
            await self.initialize()
            await self.run()
        except Exception as error:
            duration_ms = int((monotonic() - started) * 1000)
            self.logger.error("Execution of %s stopped by %s after %d ms.", name, type(error).__name__, duration_ms)
            raise
        finally:
            await self._stop_reporting(reporter, name)
            await self.close()
        self.logger.info("Executed %s in %d ms.", name, int((monotonic() - started) * 1000))
