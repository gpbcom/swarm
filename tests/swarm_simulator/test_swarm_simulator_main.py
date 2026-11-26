from __future__ import annotations

# Standard library imports
import os
import shutil
import subprocess
import sys
from importlib.metadata import entry_points
from inspect import signature
from pathlib import Path
from typing import ClassVar

# Third-party imports
import yaml

# First-party imports
from swarm_models.config.app_config import AppConfig
from swarm_simulator.main import main


class TestSwarmSimulatorMain:
    SCRIPT: ClassVar[str] = "swarm-simulator-serve"
    TARGET: ClassVar[str] = "swarm_simulator.main:main"
    APP_FOLDER: ClassVar[Path] = Path(__file__).resolve().parents[2] / "backend" / "apps" / "simulator"
    OPERATOR_ID: ClassVar[str] = "0190a5b2-7c3e-7d4f-8a1b-0000000000a0"
    OPERATOR_KEY: ClassVar[str] = "operator_id"
    NATS_KEY: ClassVar[str] = "nats"
    CREDENTIALS_KEY: ClassVar[str] = "credentials_path"
    RESPONDER_KEY: ClassVar[str] = "responder"
    SUBJECT_KEY: ClassVar[str] = "subject"
    SUBJECT: ClassVar[str] = f"op.{OPERATOR_ID}.mission.*.command"
    MISSING_CREDS: ClassVar[str] = "missing.creds"
    ENCODING: ClassVar[str] = "utf-8"
    EXIT_TIMEOUT_S: ClassVar[float] = 30.0

    def write_conf(self, work: Path) -> None:
        shutil.copytree(self.APP_FOLDER / AppConfig.CONF_FOLDER, work / AppConfig.CONF_FOLDER)
        app_file = work / AppConfig.CONF_FOLDER / AppConfig.APP_FILE
        data = yaml.safe_load(app_file.read_text(encoding=self.ENCODING))
        data[self.OPERATOR_KEY] = self.OPERATOR_ID
        data[self.NATS_KEY][self.CREDENTIALS_KEY] = str(work / self.MISSING_CREDS)
        data[self.RESPONDER_KEY][self.SUBJECT_KEY] = self.SUBJECT
        app_file.write_text(yaml.safe_dump(data), encoding=self.ENCODING)

    def test_the_console_script_points_to_main(self) -> None:
        assert entry_points(group="console_scripts")[self.SCRIPT].value == self.TARGET

    def test_main_takes_no_argument(self) -> None:
        assert not signature(main).parameters

    def test_the_configuration_of_the_app_needs_the_values_of_the_deployment(self, tmp_path: Path) -> None:
        shutil.copytree(self.APP_FOLDER / AppConfig.CONF_FOLDER, tmp_path / AppConfig.CONF_FOLDER)
        environment = dict(os.environ)
        environment[AppConfig.APP_ROOT_KEY] = str(tmp_path)

        finished = subprocess.run(
            [str(Path(sys.executable).parent / self.SCRIPT)],
            cwd=tmp_path,
            env=environment,
            capture_output=True,
            timeout=self.EXIT_TIMEOUT_S,
            check=False,
        )

        assert finished.returncode != 0

    def test_credentials_that_cannot_be_read_stop_the_app_before_it_serves(self, tmp_path: Path) -> None:
        self.write_conf(tmp_path)
        environment = dict(os.environ)
        environment[AppConfig.APP_ROOT_KEY] = str(tmp_path)

        finished = subprocess.run(
            [str(Path(sys.executable).parent / self.SCRIPT)],
            cwd=tmp_path,
            env=environment,
            capture_output=True,
            timeout=self.EXIT_TIMEOUT_S,
            check=False,
        )

        assert finished.returncode != 0
        assert b"SESimulatedCredentialsUnreadableError" in finished.stderr
