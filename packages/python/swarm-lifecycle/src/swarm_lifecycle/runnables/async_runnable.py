from __future__ import annotations

# Standard library imports
from abc import ABC, abstractmethod
from logging import Logger, getLogger
from time import monotonic
from typing import Optional


class AsyncRunnable(ABC):
    """Base class of everything that is initialised, run and closed in an event loop.

    Attributes:
        logger (Logger): Logger instance.

    Notes:
        - ``Runnable`` is a separate class and shares no base with this one, because the methods of one are plain
          methods and those of the other are coroutines, and no single signature fits both.
        - **``close`` must be safe after a failed or partial ``initialize``**, because ``execute`` always calls it.
    """

    def __init__(self, logger: Optional[Logger] = None) -> None:
        """Initialise the runnable.

        Args:
            logger (Optional[Logger]): Logger to use. A logger named after the module is used when it is ``None``.
        """
        self.logger = logger if logger else getLogger(__name__)

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

    async def execute(self) -> None:
        """Call ``initialize``, ``run`` and ``close``, and close whatever happens.

        Raises:
            Exception: Whatever ``initialize``, ``run`` or ``close`` raised, unchanged.
        """
        name = type(self).__name__
        started = monotonic()
        succeeded = False
        self.logger.debug("Executing %s.", name)
        try:
            await self.initialize()
            await self.run()
            succeeded = True
        finally:
            await self.close()
            duration_ms = int((monotonic() - started) * 1000)
            if succeeded:
                self.logger.info("Executed %s in %d ms.", name, duration_ms)
            else:
                self.logger.error("Execution of %s stopped by an error after %d ms.", name, duration_ms)
