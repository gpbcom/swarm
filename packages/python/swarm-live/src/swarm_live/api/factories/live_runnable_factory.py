from __future__ import annotations

# Standard library imports
from abc import ABC

# First-party imports
from swarm_lifecycle.factories.async_runnable_factory import AsyncRunnableFactory
from swarm_lifecycle.runnables.async_runnable import AsyncRunnable


class LiveRunnableFactory[A: AsyncRunnable](AsyncRunnableFactory[A], ABC):
    """Abstract factory of the api layer for the live runnables.

    Notes:
        - Its concrete factories are in ``api/factories/live/``.
    """
