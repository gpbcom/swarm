from __future__ import annotations

# Standard library imports
from functools import partial
from pathlib import Path
from typing import ClassVar
from uuid import UUID

# Third-party imports
from fastapi import FastAPI

# First-party imports
from swarm_models.config.simulator.simulator_config import SimulatorConfig
from swarm_models.simulation.simulations.simulation_request import SimulationRequest
from swarm_service.simulation.factories.simulations.simulation_service_factory import SimulationServiceFactory
from swarm_service.simulation.simulations.simulation_lifespan import SimulationLifespan
from tests.fakes.mavlink.helpers import MISSION_ID, a_registered_drone
from tests.fakes.mavlink.stand_in_drone import StandInDrone
from tests.fakes.mavlink.stand_in_drones import StandInDrones


class TestSimulationLifespan:
    STALL_AFTER_SEQ: ClassVar[int] = 2

    async def test_the_end_of_the_application_stops_the_flight_that_flies(
        self, stand_in_drones: StandInDrones, app_config: partial[Path]
    ) -> None:
        stalled = stand_in_drones.make(stall_after_seq=self.STALL_AFTER_SEQ)
        simulations = SimulationServiceFactory(SimulatorConfig.load(app_config([a_registered_drone(stalled)]))).create()

        async with SimulationLifespan(simulations).lifespan(FastAPI()):
            await simulations.launch(SimulationRequest(mission_id=UUID(str(MISSION_ID))))
            assert simulations.flying

        assert simulations.task is None
        assert not simulations.flying

    async def test_an_application_that_flew_nothing_stops_cleanly(
        self, stand_in_drone: StandInDrone, app_config: partial[Path]
    ) -> None:
        simulations = SimulationServiceFactory(
            SimulatorConfig.load(app_config([a_registered_drone(stand_in_drone)]))
        ).create()

        async with SimulationLifespan(simulations).lifespan(FastAPI()):
            assert not simulations.flying

        assert simulations.task is None
