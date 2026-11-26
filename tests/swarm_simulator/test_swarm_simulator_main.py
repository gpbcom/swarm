from __future__ import annotations

# Standard library imports
import subprocess
import sys
from functools import partial
from importlib.metadata import entry_points
from pathlib import Path
from typing import ClassVar, List

# Third-party imports
import pytest

# First-party imports
from services.simulator.tests.helpers import MISSION_ID, a_registered_drone
from services.simulator.tests.stand_in_drone import StandInDrone
from services.simulator.tests.stand_in_drones import StandInDrones
from simulator.models.enums import SimulatorCommandName


class TestSimulatorMain:
    SCRIPT_NAME: ClassVar[str] = "swarm-simulator"
    ENTRY_POINT: ClassVar[str] = "simulator.api.cli.main:main"
    CONFIG_FLAG: ClassVar[str] = "--config"
    MISSION_FLAG: ClassVar[str] = "--mission-id"
    CONSOLE_SCRIPTS: ClassVar[str] = "console_scripts"
    GARBAGE: ClassVar[str] = "operator_id: [not, a, mapping\n"
    ENCODING: ClassVar[str] = "utf-8"
    TIMEOUT_S: ClassVar[float] = 60.0
    STALL_AFTER_SEQ: ClassVar[int] = 2
    EXIT_OK: ClassVar[int] = 0
    EXIT_INCOMPLETE: ClassVar[int] = 1
    EXIT_USAGE: ClassVar[int] = 2

    def run_cli(self, directory: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
        script = Path(sys.executable).parent / self.SCRIPT_NAME
        return subprocess.run(
            [str(script), *arguments],
            cwd=directory,
            capture_output=True,
            text=True,
            timeout=self.TIMEOUT_S,
            check=False,
        )

    def test_the_console_script_points_at_main(self) -> None:
        scripts = {entry.name: entry.value for entry in entry_points(group=self.CONSOLE_SCRIPTS)}

        assert scripts.get(self.SCRIPT_NAME) == self.ENTRY_POINT

    def test_fly_with_two_stand_ins_exits_zero_and_prints_one_line_each(
        self, stand_in_drones: StandInDrones, app_config: partial[Path], tmp_path: Path
    ) -> None:
        stand_ins = [stand_in_drones.make(), stand_in_drones.make()]
        drones = [a_registered_drone(stand_in, index) for index, stand_in in enumerate(stand_ins)]
        config = app_config(drones)

        result = self.run_cli(
            tmp_path, SimulatorCommandName.FLY, self.CONFIG_FLAG, str(config), self.MISSION_FLAG, MISSION_ID
        )

        assert result.returncode == self.EXIT_OK
        assert len(result.stdout.splitlines()) == len(stand_ins)

    def test_fly_with_one_stalled_stand_in_exits_one(
        self, stand_in_drones: StandInDrones, app_config: partial[Path], tmp_path: Path
    ) -> None:
        stand_ins = [stand_in_drones.make(), stand_in_drones.make(stall_after_seq=self.STALL_AFTER_SEQ)]
        drones = [a_registered_drone(stand_in, index) for index, stand_in in enumerate(stand_ins)]
        config = app_config(drones)

        result = self.run_cli(
            tmp_path, SimulatorCommandName.FLY, self.CONFIG_FLAG, str(config), self.MISSION_FLAG, MISSION_ID
        )

        assert result.returncode == self.EXIT_INCOMPLETE
        assert len(result.stdout.splitlines()) == len(stand_ins)

    def test_a_missing_config_exits_two(self, tmp_path: Path) -> None:
        missing = tmp_path / "missing.yaml"

        result = self.run_cli(
            tmp_path, SimulatorCommandName.FLY, self.CONFIG_FLAG, str(missing), self.MISSION_FLAG, MISSION_ID
        )

        assert result.returncode == self.EXIT_USAGE

    def test_an_invalid_config_exits_two(self, tmp_path: Path) -> None:
        config = tmp_path / "broken.yaml"
        config.write_text(self.GARBAGE, encoding=self.ENCODING)

        result = self.run_cli(
            tmp_path, SimulatorCommandName.FLY, self.CONFIG_FLAG, str(config), self.MISSION_FLAG, MISSION_ID
        )

        assert result.returncode == self.EXIT_USAGE

    def test_a_missing_mission_id_exits_two(
        self, stand_in_drone: StandInDrone, app_config: partial[Path], tmp_path: Path
    ) -> None:
        config = app_config([a_registered_drone(stand_in_drone)])

        result = self.run_cli(tmp_path, SimulatorCommandName.FLY, self.CONFIG_FLAG, str(config))

        assert result.returncode == self.EXIT_USAGE

    @pytest.mark.parametrize("arguments", [[], ["dance"]])
    def test_a_missing_or_unknown_command_exits_two(self, tmp_path: Path, arguments: List[str]) -> None:
        result = self.run_cli(tmp_path, *arguments)

        assert result.returncode == self.EXIT_USAGE
