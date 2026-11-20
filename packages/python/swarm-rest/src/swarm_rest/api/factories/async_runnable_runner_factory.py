from __future__ import annotations

# Standard library imports
from logging import Logger, getLogger
from typing import Optional

# First-party imports
from swarm_lifecycle.factories.runnable_factory import RunnableFactory
from swarm_lifecycle.runnables.async_runnable import AsyncRunnable
from swarm_rest.api.cli.async_runnable_runner import AsyncRunnableRunner


class AsyncRunnableRunnerFactory(RunnableFactory[AsyncRunnableRunner]):
    """Builds runners of one async runnable.

    Attributes:
        runnable (AsyncRunnable): The runnable each runner runs.
    """

    def __init__(self, runnable: AsyncRunnable, logger: Optional[Logger] = None) -> None:
        """Initialise the factory.

        Args:
            runnable (AsyncRunnable): The runnable each runner runs.
            logger (Optional[Logger]): Logger to use. A logger named after the module is used when it is ``None``.
        """
        super().__init__()
        self.logger = logger if logger else getLogger(__name__)
        self.runnable = runnable

    ############################
    # Internal Helpers Methods #
    ############################

    def _build(self) -> AsyncRunnableRunner:
        """Build one runner.

        Returns:
            AsyncRunnableRunner: A new runner of the runnable.
        """
        self.logger.debug("Building a runner of %s.", type(self.runnable).__name__)
        return AsyncRunnableRunner(self.runnable)
