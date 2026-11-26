from __future__ import annotations

# Third-party imports
from lifecycle_sample_runnable import SampleRunnable

# First-party imports
from swarm_lifecycle.factories.runnable_factory import RunnableFactory


class SampleRunnableFactory(RunnableFactory[SampleRunnable]):
    """Builds sample runnables."""

    ############################
    # Internal Helpers Methods #
    ############################

    def _build(self) -> SampleRunnable:
        """Build one sample.

        Returns:
            SampleRunnable: A new sample.
        """
        return SampleRunnable()
