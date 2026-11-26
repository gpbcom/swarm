from __future__ import annotations

# Standard library imports
from abc import ABC

# First-party imports
from swarm_lifecycle.factories.async_runnable_factory import AsyncRunnableFactory
from swarm_lifecycle.runnables.async_runnable import AsyncRunnable


class BusRunnableFactory[A: AsyncRunnable](AsyncRunnableFactory[A], ABC):
    """Abstract factory of the service layer for the bus runnables, responders and consumers.

    Notes:
        - Its concrete factories are in ``api/factories/bus/``.
    """
