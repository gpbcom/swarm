from __future__ import annotations

# Standard library imports
from functools import partial
from pathlib import Path
from uuid import UUID

# First-party imports
from services.simulator.tests.helpers import MISSION_ID, a_registered_drone
from services.simulator.tests.stand_in_drone import StandInDrone
from simulator.api.cli.commands.fly_command import FlyCommand
from simulator.api.factories.command_factory import CommandFactory
from simulator.api.factories.fly.fly_command_factory import FlyCommandFactory
from simulator.models.config.simulator_config import SimulatorConfig
from swarm_lifecycle.factories.runnable_factory import RunnableFactory


class TestFlyCommandFactory:
    def factory(self, stand_in_drone: StandInDrone, app_config: partial[Path]) -> FlyCommandFactory:
        config = SimulatorConfig.load(app_config([a_registered_drone(stand_in_drone)]))
        return FlyCommandFactory(config, UUID(str(MISSION_ID)))

    def test_create_returns_a_fly_command(self, stand_in_drone: StandInDrone, app_config: partial[Path]) -> None:
        assert isinstance(self.factory(stand_in_drone, app_config).create(), FlyCommand)

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
