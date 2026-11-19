from __future__ import annotations

# Standard library imports
from abc import ABC

# First-party imports
from swarm_lifecycle.factories.factory import Factory
from swarm_lifecycle.runnables.runnable import Runnable


class RunnableFactory[R: Runnable](Factory[R], ABC):
    """Abstract factory of runnables.

    Notes:
        - A layer's abstract factory, such as ``CommandFactory`` in ``api/factories/``, subclasses this class.
    """
