from __future__ import annotations

# Standard library imports
from functools import partial
from pathlib import Path

# First-party imports
from services.simulator.tests.helpers import a_registered_drone
from services.simulator.tests.stand_in_drone import StandInDrone
from simulator.api.cli.commands.serve_command import ServeCommand
from simulator.api.factories.command_factory import CommandFactory
from simulator.api.factories.serve.serve_command_factory import ServeCommandFactory
from simulator.models.config.simulator_config import SimulatorConfig
from swarm_lifecycle.factories.runnable_factory import RunnableFactory


class TestServeCommandFactory:
    def factory(self, stand_in_drone: StandInDrone, app_config: partial[Path]) -> ServeCommandFactory:
        config = SimulatorConfig.load(app_config([a_registered_drone(stand_in_drone)]))
        return ServeCommandFactory(config)

    def test_create_returns_a_serve_command(self, stand_in_drone: StandInDrone, app_config: partial[Path]) -> None:
        assert isinstance(self.factory(stand_in_drone, app_config).create(), ServeCommand)

    def test_create_returns_a_new_command_on_each_call(
        self, stand_in_drone: StandInDrone, app_config: partial[Path]
    ) -> None:
        factory = self.factory(stand_in_drone, app_config)

        assert factory.create() is not factory.create()

    def test_the_factory_is_a_command_factory_and_a_runnable_factory(
        self, stand_in_drone: StandInDrone, app_config: partial[Path]
    ) -> None:
        factory = self.factory(stand_in_drone, app_config)

        assert isinstance(factory, CommandFactory)
        assert isinstance(factory, RunnableFactory)
