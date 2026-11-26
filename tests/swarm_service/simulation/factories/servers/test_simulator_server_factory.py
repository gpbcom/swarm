from __future__ import annotations

# Standard library imports
from functools import partial
from pathlib import Path

# Third-party imports
from fastapi import FastAPI

# First-party imports
from swarm_lifecycle.factories.async_runnable_factory import AsyncRunnableFactory
from swarm_lifecycle.runnables.async_runnable import AsyncRunnable
from swarm_models.config.simulator.simulator_config import SimulatorConfig
from swarm_service.simulation.factories.server_factory import ServerFactory
from swarm_service.simulation.factories.servers.simulator_server_factory import SimulatorServerFactory
from swarm_service.simulation.servers.simulator_server import SimulatorServer
from tests.fakes.mavlink.helpers import a_registered_drone
from tests.fakes.mavlink.stand_in_drone import StandInDrone


class TestSimulatorServerFactory:
    def factory(self, stand_in_drone: StandInDrone, app_config: partial[Path]) -> SimulatorServerFactory:
        config = SimulatorConfig.load(app_config([a_registered_drone(stand_in_drone)]))
        return SimulatorServerFactory(config, FastAPI())

    def test_create_returns_the_runnable_of_the_responder_and_the_server_of_the_app(
        self, stand_in_drone: StandInDrone, app_config: partial[Path]
    ) -> None:
        factory = self.factory(stand_in_drone, app_config)

        server = factory.create()

        assert isinstance(server, SimulatorServer)
        assert isinstance(server, AsyncRunnable)
        assert server.server_factory.app is factory.app
        assert server.server_factory.config == factory.config.rest
        assert server.status_interval_s == factory.config.rest.status_interval_s

    def test_create_returns_a_new_runnable_on_each_call(
        self, stand_in_drone: StandInDrone, app_config: partial[Path]
    ) -> None:
        factory = self.factory(stand_in_drone, app_config)

        assert factory.create() is not factory.create()

    def test_the_factory_is_a_server_factory(self, stand_in_drone: StandInDrone, app_config: partial[Path]) -> None:
        factory = self.factory(stand_in_drone, app_config)

        assert isinstance(factory, ServerFactory)
        assert isinstance(factory, AsyncRunnableFactory)
