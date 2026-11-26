from __future__ import annotations

# Standard library imports
from abc import ABC

# First-party imports
from swarm_lifecycle.factories.async_runnable_factory import AsyncRunnableFactory
from swarm_lifecycle.runnables.async_runnable import AsyncRunnable


class ServerFactory[A: AsyncRunnable](AsyncRunnableFactory[A], ABC):
    """Abstract factory of the service layer for the runnables that serve the simulator app.

    Notes:
        - Concrete factories, in ``factories/servers/``, implement ``_build`` and callers use ``create``.
    """
