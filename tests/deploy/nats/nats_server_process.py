from __future__ import annotations

# Standard library imports
import socket
import subprocess
import time
from pathlib import Path
from typing import ClassVar, Optional


class NatsServerProcess:
    """A real ``nats-server`` process, started from a configuration text and killed after the test."""

    READY_TIMEOUT_S: ClassVar[float] = 10.0
    POLL_INTERVAL_S: ClassVar[float] = 0.05
    KILL_TIMEOUT_S: ClassVar[float] = 5.0
    CONFIG_NAME: ClassVar[str] = "nats.conf"
    LOG_NAME: ClassVar[str] = "nats.log"
    HOST: ClassVar[str] = "127.0.0.1"
    BINARY: ClassVar[str] = "nats-server"
    CONFIG_FLAG: ClassVar[str] = "-c"
    ENCODING: ClassVar[str] = "utf-8"

    def __init__(self, workdir: Path, config: str, port: int) -> None:
        self.workdir = workdir
        self.config = config
        self.port = port
        self.process: Optional[subprocess.Popen[bytes]] = None

    ############################
    # Internal Helpers Methods #
    ############################

    def _accepts(self) -> bool:
        try:
            with socket.create_connection((self.HOST, self.port), timeout=0.2):
                return True
        except OSError:
            return False

    def _output(self) -> str:
        log = self.workdir / self.LOG_NAME
        if log.exists():
            return log.read_text(encoding=self.ENCODING)
        return ""

    ############################
    # Publicly Exposed Methods #
    ############################

    @property
    def url(self) -> str:
        return f"nats://{self.HOST}:{self.port}"

    def spawn(self) -> None:
        """Write the configuration, start the server and wait until its port accepts."""
        self.workdir.mkdir(parents=True, exist_ok=True)
        path = self.workdir / self.CONFIG_NAME
        path.write_text(self.config, encoding=self.ENCODING)
        log = (self.workdir / self.LOG_NAME).open("wb")
        self.process = subprocess.Popen([self.BINARY, self.CONFIG_FLAG, str(path)], stdout=log, stderr=log)
        deadline = time.monotonic() + self.READY_TIMEOUT_S
        while time.monotonic() < deadline:
            if self.process.poll() is not None:
                break
            if self._accepts():
                return
            time.sleep(self.POLL_INTERVAL_S)
        output = self._output()
        self.kill()
        raise AssertionError(f"nats-server did not become ready on port {self.port}. Output: {output}")

    def kill(self) -> None:
        """Terminate the server and wait for it."""
        if self.process is None:
            return
        self.process.terminate()
        try:
            self.process.wait(timeout=self.KILL_TIMEOUT_S)
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.process.wait()
        self.process = None
