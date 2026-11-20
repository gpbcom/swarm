from __future__ import annotations

# Standard library imports
from abc import ABC

# First-party imports
from swarm_lifecycle.factories.async_runnable_factory import AsyncRunnableFactory
from swarm_lifecycle.runnables.async_runnable import AsyncRunnable


class FlightFactory[A: AsyncRunnable](AsyncRunnableFactory[A], ABC):
    """Abstract factory of the flights of the service layer.

    Notes:
        - Concrete factories, in ``factories/flights/``, implement ``_build`` and callers use ``create``.
    """
