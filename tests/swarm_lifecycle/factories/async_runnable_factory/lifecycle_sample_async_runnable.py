from __future__ import annotations

# Standard library imports
from typing import ClassVar

# First-party imports
from swarm_lifecycle.runnables.async_runnable import AsyncRunnable


class SampleAsyncRunnable(AsyncRunnable):
    """A stand-in async_runnable that records that it ran.

    Attributes:
        STATUS_INTERVAL_S (float): Seconds between two status reports.
        executed (bool): Whether ``run`` has been called.
    """

    STATUS_INTERVAL_S: ClassVar[float] = 60.0

    def __init__(self) -> None:
        """Create a sample that has not run yet."""
        super().__init__(self.STATUS_INTERVAL_S)
        self.executed = False

    ############################
    # Publicly Exposed Methods #
    ############################

    async def initialize(self) -> None:
        """Do nothing."""

    async def run(self) -> None:
        """Record that the work was done."""
        self.executed = True

    async def close(self) -> None:
        """Do nothing."""
