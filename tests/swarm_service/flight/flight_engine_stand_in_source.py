from __future__ import annotations

# Standard library imports
from typing import List, Optional

# First-party imports
from flight_engine.clients.mavlink.sample_source import SampleSource
from flight_engine.models.telemetry.drone_sample import DroneSample


class StandInSampleSource(SampleSource):
    """A source of Drone samples that returns the ones a test sets.

    Attributes:
        samples (List[DroneSample]): The samples the next snapshot returns.
        opened (bool): Whether ``open`` was called.
        closed (bool): Whether ``close`` was called.
        snapshots (int): How many snapshots were taken.
    """

    def __init__(self, samples: Optional[List[DroneSample]] = None) -> None:
        self.samples: List[DroneSample] = list(samples) if samples else []
        self.opened = False
        self.closed = False
        self.snapshots = 0

    async def open(self) -> None:
        self.opened = True

    def snapshot(self) -> List[DroneSample]:
        self.snapshots += 1
        return list(self.samples)

    async def close(self) -> None:
        self.closed = True
