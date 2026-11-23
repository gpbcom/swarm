from __future__ import annotations

# Standard library imports
from typing import Iterator

# Third-party imports
import pytest

# First-party imports
from services.simulator.tests.stand_in_drone import StandInDrone
from services.simulator.tests.stand_in_drones import StandInDrones


@pytest.fixture
def stand_in_drones() -> Iterator[StandInDrones]:
    drones = StandInDrones()
    yield drones
    drones.close_all()


@pytest.fixture
def stand_in_drone(stand_in_drones: StandInDrones) -> StandInDrone:
    return stand_in_drones.make()
