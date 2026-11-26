from __future__ import annotations

# Standard library imports
from functools import partial
from pathlib import Path
from typing import ClassVar
from uuid import UUID

# Third-party imports
import pytest

# First-party imports
from services.simulator.tests.helpers import MISSION_ID, a_registered_drone
from services.simulator.tests.stand_in_drones import StandInDrones
from simulator.api.cli.commands.fly_command import FlyCommand
from simulator.api.factories.fly.fly_command_factory import FlyCommandFactory
from simulator.models.config.simulator_config import SimulatorConfig
from swarm_lifecycle.runnables.runnable import Runnable


class TestFlyCommand:
    STALL_AFTER_SEQ: ClassVar[int] = 2
    EXIT_OK: ClassVar[int] = 0
    EXIT_INCOMPLETE: ClassVar[int] = 1

    def command(self, config_path: Path) -> FlyCommand:
        config = SimulatorConfig.load(config_path)
        command = FlyCommandFactory(config, UUID(str(MISSION_ID))).create()
        assert isinstance(command, FlyCommand)
        return command

    def test_it_is_a_runnable(self) -> None:
        assert issubclass(FlyCommand, Runnable)

    def test_two_completed_flights_exit_zero_and_print_one_line_each(
        self,
        stand_in_drones: StandInDrones,
        app_config: partial[Path],
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        stand_ins = [stand_in_drones.make(), stand_in_drones.make()]
        command = self.command(app_config([a_registered_drone(s, i) for i, s in enumerate(stand_ins)]))

        command.execute()

        assert command.exit_code == self.EXIT_OK
        assert len(capsys.readouterr().out.splitlines()) == len(stand_ins)

    def test_a_stalled_flight_exits_one_and_still_prints_every_outcome(
        self,
        stand_in_drones: StandInDrones,
        app_config: partial[Path],
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        stand_ins = [stand_in_drones.make(), stand_in_drones.make(stall_after_seq=self.STALL_AFTER_SEQ)]
        command = self.command(app_config([a_registered_drone(s, i) for i, s in enumerate(stand_ins)]))

        command.execute()

        assert command.exit_code == self.EXIT_INCOMPLETE
        assert len(capsys.readouterr().out.splitlines()) == len(stand_ins)
