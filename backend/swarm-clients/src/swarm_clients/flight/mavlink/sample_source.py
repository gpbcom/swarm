from __future__ import annotations

# Standard library imports
from abc import ABC, abstractmethod
from typing import List

# First-party imports
from flight_engine.models.telemetry.drone_sample import DroneSample


class SampleSource(ABC):
    """Where the flight engine reads the latest sample of each Drone from."""

    @abstractmethod
    async def open(self) -> None:
        """Start receiving Drone frames."""

    @abstractmethod
    def snapshot(self) -> List[DroneSample]:
        """Give the latest sample of every Drone heard from.

        Returns:
            List[DroneSample]: The samples, ordered by system id.
        """

    @abstractmethod
    async def close(self) -> None:
        """Stop receiving Drone frames and release the port."""
