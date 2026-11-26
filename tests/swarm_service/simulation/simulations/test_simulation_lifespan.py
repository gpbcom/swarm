from __future__ import annotations

# Standard library imports
from functools import partial
from pathlib import Path
from typing import ClassVar, Tuple

# Third-party imports
import pytest
from fastapi import FastAPI

# First-party imports
from swarm_models.config.simulator.simulator_config import SimulatorConfig
from swarm_models.simulation.credentials.exceptions import (
    SESimulatedCredentialsNotSimulatedError,
    SESimulatedCredentialsUnreadableError,
)
from swarm_service.simulation.factories.simulations.simulation_service_factory import SimulationServiceFactory
from swarm_service.simulation.simulations.simulation_lifespan import SimulationLifespan
from tests.fakes.mavlink.helpers import a_registered_drone
from tests.fakes.mavlink.stand_in_drone import StandInDrone
from tests.infra.nats.helpers import connz_users

Cell = Tuple[str, int, Path, Path]


class TestSimulationLifespan:
    MISSING_CREDS: ClassVar[str] = "missing.creds"

    def a_lifespan(self, config: SimulatorConfig) -> SimulationLifespan:
        return SimulationLifespan(config, SimulationServiceFactory(config).create())

    async def test_service_credentials_stop_the_start_before_anything_connects(
        self, nats_cell: Cell, stand_in_drone: StandInDrone, app_config: partial[Path]
    ) -> None:
        url, monitor_port, _, service_creds = nats_cell
        config = SimulatorConfig.load(app_config([a_registered_drone(stand_in_drone)], server=url, creds=service_creds))
        lifespan = self.a_lifespan(config)

        with pytest.raises(SESimulatedCredentialsNotSimulatedError):
            async with lifespan.lifespan(FastAPI()):
                pass

        assert lifespan.task is None
        assert connz_users(monitor_port) == []

    async def test_an_unreadable_credentials_file_stops_the_start(
        self, stand_in_drone: StandInDrone, app_config: partial[Path], tmp_path: Path
    ) -> None:
        drones = [a_registered_drone(stand_in_drone)]
        config = SimulatorConfig.load(app_config(drones, creds=tmp_path / self.MISSING_CREDS))

        with pytest.raises(SESimulatedCredentialsUnreadableError):
            async with self.a_lifespan(config).lifespan(FastAPI()):
                pass

    async def test_simulated_credentials_start_the_responder_and_stopping_cancels_it(
        self, nats_cell: Cell, stand_in_drone: StandInDrone, app_config: partial[Path]
    ) -> None:
        url, _, simulated_creds, _ = nats_cell
        config = SimulatorConfig.load(
            app_config([a_registered_drone(stand_in_drone)], server=url, creds=simulated_creds)
        )
        lifespan = self.a_lifespan(config)

        async with lifespan.lifespan(FastAPI()):
            assert lifespan.task is not None
            assert not lifespan.task.done()

        assert lifespan.task is None
