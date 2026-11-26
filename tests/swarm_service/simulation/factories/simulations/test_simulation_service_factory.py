from __future__ import annotations

# Standard library imports
from functools import partial
from pathlib import Path

# First-party imports
from swarm_lifecycle.factories.factory import Factory
from swarm_models.config.simulator.simulator_config import SimulatorConfig
from swarm_service.simulation.factories.simulations.simulation_service_factory import SimulationServiceFactory
from swarm_service.simulation.simulations.simulation_service import SimulationService
from tests.fakes.mavlink.helpers import a_registered_drone
from tests.fakes.mavlink.stand_in_drone import StandInDrone


class TestSimulationServiceFactory:
    def factory(self, stand_in_drone: StandInDrone, app_config: partial[Path]) -> SimulationServiceFactory:
        config = SimulatorConfig.load(app_config([a_registered_drone(stand_in_drone)]))
        return SimulationServiceFactory(config)

    def test_create_returns_a_service_with_no_flight(
        self, stand_in_drone: StandInDrone, app_config: partial[Path]
    ) -> None:
        service = self.factory(stand_in_drone, app_config).create()

        assert isinstance(service, SimulationService)
        assert service.flight is None
        assert service.flying is False

    def test_create_returns_a_new_service_on_each_call(
        self, stand_in_drone: StandInDrone, app_config: partial[Path]
    ) -> None:
        factory = self.factory(stand_in_drone, app_config)

        assert factory.create() is not factory.create()
        assert isinstance(factory, Factory)
