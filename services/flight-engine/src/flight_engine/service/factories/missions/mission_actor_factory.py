from __future__ import annotations

# Standard library imports
from abc import ABC

# First-party imports
from flight_engine.service.missions.mission_actor import MissionActor
from swarm_lifecycle.factories.async_runnable_factory import AsyncRunnableFactory


class MissionActorFactory(AsyncRunnableFactory[MissionActor], ABC):
    """Abstract factory of the Mission actors of the flight engine.

    Notes:
        - Its concrete factories are in ``service/factories/missions/actors/``.
    """
