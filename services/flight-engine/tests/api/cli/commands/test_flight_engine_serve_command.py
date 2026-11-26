from __future__ import annotations

# Standard library imports
import signal
import socket
import subprocess
import sys
import time
from pathlib import Path
from typing import ClassVar

# Third-party imports
import pytest
from websockets.sync.client import connect

pytest.importorskip("swarm_core")

# First-party imports
from flight_engine.api.cli.commands.serve_command import ServeCommand  # isort: skip
from flight_engine.api.factories.serve.serve_command_factory import ServeCommandFactory  # isort: skip
from swarm_lifecycle.runnables.runnable import Runnable  # isort: skip


class TestServeCommand:
    HOST: ClassVar[str] = "127.0.0.1"
    PATH: ClassVar[str] = "/v1/live"
    CONFIG_NAME: ClassVar[str] = "app.yaml"
    MISSIONS_NAME: ClassVar[str] = "missions.yaml"
    ENCODING: ClassVar[str] = "utf-8"
    LAUNCH: ClassVar[str] = "import sys; from flight_engine.api.cli.main import main; sys.argv = sys.argv[1:]; main()"
    PROGRAM: ClassVar[str] = "swarm-flight-engine"
    CONFIG_FLAG: ClassVar[str] = "--config"
    READY_TIMEOUT_S: ClassVar[float] = 30.0
    EXIT_TIMEOUT_S: ClassVar[float] = 20.0
    OPEN_TIMEOUT_S: ClassVar[float] = 1.0
    POLL_S: ClassVar[float] = 0.1

    def free_port(self) -> int:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
            probe.bind((self.HOST, 0))
            return int(probe.getsockname()[1])

    def test_the_command_is_a_runnable_built_by_its_factory(self, tmp_path: Path) -> None:
        command = ServeCommandFactory(tmp_path / self.CONFIG_NAME).create()

        assert isinstance(command, ServeCommand)
        assert isinstance(command, Runnable)

    def test_the_served_engine_accepts_a_websocket_and_stops_on_sigint_with_zero(
        self, tmp_path: Path, nats_url: str
    ) -> None:
        port = self.free_port()
        missions = tmp_path / self.MISSIONS_NAME
        missions.write_text("missions: []\n", encoding=self.ENCODING)
        config = tmp_path / self.CONFIG_NAME
        config.write_text(
            f"missions_catalog_path: {missions}\n"
            f"nats:\n  servers: ['{nats_url}']\n"
            f"live:\n  host: {self.HOST}\n  port: {port}\n",
            encoding=self.ENCODING,
        )
        process = subprocess.Popen(
            [sys.executable, "-c", self.LAUNCH, self.PROGRAM, self.CONFIG_FLAG, str(config)],
            cwd=tmp_path,
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
            process.send_signal(signal.SIGINT)
            code = process.wait(timeout=self.EXIT_TIMEOUT_S)
        finally:
            if process.poll() is None:
                process.kill()

        assert connected
        assert code == 0
