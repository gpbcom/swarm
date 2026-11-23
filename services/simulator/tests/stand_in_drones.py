from __future__ import annotations

# Standard library imports
from typing import List, Union

# First-party imports
from services.simulator.tests.stand_in_drone import StandInDrone


class StandInDrones:
    """Creates stand-in Drones and closes every one of them together."""

    def __init__(self) -> None:
        self.drones: List[StandInDrone] = []

    def make(self, **options: Union[float, bool, None]) -> StandInDrone:
        drone = StandInDrone(**options)
        drone.__enter__()
        self.drones.append(drone)
        return drone

    def close_all(self) -> None:
        for drone in self.drones:
            drone.__exit__(None, None, None)
        self.drones.clear()
