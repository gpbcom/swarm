from __future__ import annotations

# First-party imports
from swarm_lifecycle.runnables.runnable import Runnable


class SampleRunnable(Runnable):
    """A stand-in runnable that records that it ran.

    Attributes:
        executed (bool): Whether ``run`` has been called.
    """

    def __init__(self) -> None:
        """Create a sample that has not run yet."""
        super().__init__()
        self.executed = False

    ############################
    # Publicly Exposed Methods #
    ############################

    def initialize(self) -> None:
        """Do nothing."""

    def run(self) -> None:
        """Record that the work was done."""
        self.executed = True

    def close(self) -> None:
        """Do nothing."""
