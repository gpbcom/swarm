from __future__ import annotations

# Standard library imports
from abc import ABC, abstractmethod
from uuid import UUID


class FrameSink(ABC):
    """Where the flight engine sends the encoded SquadFrame of each tick."""

    @abstractmethod
    async def publish(self, operator_id: UUID, mission_id: UUID, data: bytes) -> None:
        """Send one encoded SquadFrame.

        Args:
            operator_id (UUID): The Operator of the Mission.
            mission_id (UUID): The Mission the frame belongs to.
            data (bytes): The encoded frame.
        """
