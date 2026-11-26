from __future__ import annotations

# Third-party imports
from lifecycle_sample_async_runnable import SampleAsyncRunnable

# First-party imports
from swarm_lifecycle.factories.async_runnable_factory import AsyncRunnableFactory


class SampleAsyncRunnableFactory(AsyncRunnableFactory[SampleAsyncRunnable]):
    """Builds sample async_runnables."""

    ############################
    # Internal Helpers Methods #
    ############################

    def _build(self) -> SampleAsyncRunnable:
        """Build one sample.

        Returns:
            SampleAsyncRunnable: A new sample.
        """
        return SampleAsyncRunnable()
