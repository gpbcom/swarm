from __future__ import annotations

# Standard library imports
from functools import partial
from pathlib import Path

# First-party imports
from swarm_lifecycle.factories.async_runnable_factory import AsyncRunnableFactory
from swarm_models.config.simulator.simulator_config import SimulatorConfig
from swarm_service.shared.bus.factories.bus_runnable_factory import BusRunnableFactory
from swarm_service.simulation.bus.command_responder import CommandResponder
from swarm_service.simulation.drones.drone_service import DroneService
from swarm_service.simulation.factories.bus.command_responder_factory import CommandResponderFactory
from tests.fakes.mavlink.helpers import a_registered_drone
from tests.fakes.mavlink.stand_in_drone import StandInDrone


class TestCommandResponderFactory:
    def factory(self, stand_in_drone: StandInDrone, app_config: partial[Path]) -> CommandResponderFactory:
        config = SimulatorConfig.load(app_config([a_registered_drone(stand_in_drone)]))
        return CommandResponderFactory(config)

    def test_create_returns_a_responder_with_its_own_drone_service(
        self, stand_in_drone: StandInDrone, app_config: partial[Path]
    ) -> None:
        responder = self.factory(stand_in_drone, app_config).create()

        assert isinstance(responder, CommandResponder)
        assert isinstance(responder.service, DroneService)
        assert responder.client is None

    def test_create_returns_a_new_responder_on_each_call(
        self, stand_in_drone: StandInDrone, app_config: partial[Path]
    ) -> None:
        factory = self.factory(stand_in_drone, app_config)

        assert factory.create() is not factory.create()

    def test_the_factory_is_a_bus_runnable_factory(
        self, stand_in_drone: StandInDrone, app_config: partial[Path]
    ) -> None:
        factory = self.factory(stand_in_drone, app_config)

        assert isinstance(factory, BusRunnableFactory)
        assert isinstance(factory, AsyncRunnableFactory)
