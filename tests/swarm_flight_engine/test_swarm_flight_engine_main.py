from __future__ import annotations

# Standard library imports
import os
import shutil
import signal
import socket
import subprocess
import sys
import time
from importlib.metadata import entry_points
from inspect import signature
from pathlib import Path
from typing import ClassVar

# Third-party imports
import pytest
import yaml
from websockets.sync.client import connect

pytest.importorskip("swarm_core")

# First-party imports
from swarm_flight_engine.main import main
from swarm_models.config.app_config import AppConfig


class TestSwarmFlightEngineMain:
    SCRIPT: ClassVar[str] = "swarm-flight-engine-serve"
    TARGET: ClassVar[str] = "swarm_flight_engine.main:main"
    APP_FOLDER: ClassVar[Path] = Path(__file__).resolve().parents[2] / "backend" / "apps" / "flight-engine"
    HOST: ClassVar[str] = "127.0.0.1"
    PATH: ClassVar[str] = "/v1/live"
    MISSIONS_KEY: ClassVar[str] = "missions_catalog_path"
    NATS_KEY: ClassVar[str] = "nats"
    SERVERS_KEY: ClassVar[str] = "servers"
    LIVE_KEY: ClassVar[str] = "live"
    HOST_KEY: ClassVar[str] = "host"
    PORT_KEY: ClassVar[str] = "port"
    MISSIONS_NAME: ClassVar[str] = "missions.yaml"
    ENCODING: ClassVar[str] = "utf-8"
    READY_TIMEOUT_S: ClassVar[float] = 30.0
    EXIT_TIMEOUT_S: ClassVar[float] = 20.0
    OPEN_TIMEOUT_S: ClassVar[float] = 1.0
    POLL_S: ClassVar[float] = 0.1

    def free_port(self) -> int:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
            probe.bind((self.HOST, 0))
            return int(probe.getsockname()[1])

    def write_conf(self, work: Path, nats_url: str, port: int) -> None:
        shutil.copytree(self.APP_FOLDER / AppConfig.CONF_FOLDER, work / AppConfig.CONF_FOLDER)
        missions = work / self.MISSIONS_NAME
        missions.write_text("missions: []\n", encoding=self.ENCODING)
        app_file = work / AppConfig.CONF_FOLDER / AppConfig.APP_FILE
        data = yaml.safe_load(app_file.read_text(encoding=self.ENCODING))
        data[self.MISSIONS_KEY] = str(missions)
        data[self.NATS_KEY][self.SERVERS_KEY] = [nats_url]
        data[self.LIVE_KEY][self.HOST_KEY] = self.HOST
        data[self.LIVE_KEY][self.PORT_KEY] = port
        app_file.write_text(yaml.safe_dump(data), encoding=self.ENCODING)

    def test_the_console_script_points_to_main(self) -> None:
        assert entry_points(group="console_scripts")[self.SCRIPT].value == self.TARGET

    def test_main_takes_no_argument(self) -> None:
        assert not signature(main).parameters

    def test_the_app_serves_its_live_socket_from_the_folder_the_entry_names_until_it_is_stopped(
        self, tmp_path: Path, nats_url: str
    ) -> None:
        port = self.free_port()
        self.write_conf(tmp_path, nats_url, port)
        environment = dict(os.environ)
        environment[AppConfig.APP_ROOT_KEY] = str(tmp_path)
        process = subprocess.Popen(
            [str(Path(sys.executable).parent / self.SCRIPT)],
            cwd=tmp_path,
            env=environment,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        connected = False
        try:
            deadline = time.monotonic() + self.READY_TIMEOUT_S
            while time.monotonic() < deadline and not connected and process.poll() is None:
                try:
                    with connect(f"ws://{self.HOST}:{port}{self.PATH}", open_timeout=self.OPEN_TIMEOUT_S):
                        connected = True
                except OSError:
                    time.sleep(self.POLL_S)
            process.send_signal(signal.SIGTERM)
            process.wait(timeout=self.EXIT_TIMEOUT_S)
        finally:
            if process.poll() is None:
                process.kill()
                process.wait()

        assert connected
        assert process.returncode is not None
