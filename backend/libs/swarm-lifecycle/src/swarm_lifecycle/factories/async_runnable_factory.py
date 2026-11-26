from __future__ import annotations

# Standard library imports
from abc import ABC

# First-party imports
from swarm_lifecycle.factories.factory import Factory
from swarm_lifecycle.runnables.async_runnable import AsyncRunnable


class AsyncRunnableFactory[A: AsyncRunnable](Factory[A], ABC):
    """Abstract factory of asynchronous runnables.

    Notes:
        - A layer's abstract factory, such as ``CommandFactory`` in ``api/factories/``, subclasses this class.
    """
