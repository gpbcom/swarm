from __future__ import annotations

# Standard library imports
import os
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path
from types import TracebackType
from typing import ClassVar, Optional, Self, Type

# Third-party imports
import httpx
import yaml

# First-party imports
from swarm_models.config.app_config import AppConfig


class AppServer:
    """Serves an app with its console script, in a child process, from a copy of its folder on a free port.

    The copy is the app's ``conf/`` with ``rest.host`` and ``rest.port`` changed, and the child runs in it with
    ``SWARM_APP_ROOT`` set, as the image runs the app from ``/app``.
    """

    HOST: ClassVar[str] = "127.0.0.1"
    REST_KEY: ClassVar[str] = "rest"
    HOST_KEY: ClassVar[str] = "host"
    PORT_KEY: ClassVar[str] = "port"
    OPENAPI_PATH: ClassVar[str] = "/v1/openapi.json"
    ENCODING: ClassVar[str] = "utf-8"
    START_TIMEOUT_S: ClassVar[float] = 30.0
    POLL_INTERVAL_S: ClassVar[float] = 0.1
    STOP_TIMEOUT_S: ClassVar[float] = 10.0

    def __init__(self, script: str, app_folder: Path, work: Path) -> None:
        self.script = script
        self.app_folder = app_folder
        self.work = work
        self.port = self.free_port()
        self.process: Optional[subprocess.Popen[bytes]] = None

    def free_port(self) -> int:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
            probe.bind((self.HOST, 0))
            port: int = probe.getsockname()[1]
        return port

    @property
    def url(self) -> str:
        return f"http://{self.HOST}:{self.port}"

    def write_conf(self) -> None:
        shutil.copytree(self.app_folder / AppConfig.CONF_FOLDER, self.work / AppConfig.CONF_FOLDER)
        app_file = self.work / AppConfig.CONF_FOLDER / AppConfig.APP_FILE
        data = yaml.safe_load(app_file.read_text(encoding=self.ENCODING))
        data[self.REST_KEY][self.HOST_KEY] = self.HOST
        data[self.REST_KEY][self.PORT_KEY] = self.port
        app_file.write_text(yaml.safe_dump(data), encoding=self.ENCODING)

    def get_openapi(self) -> httpx.Response:
        return httpx.get(self.url + self.OPENAPI_PATH, timeout=self.POLL_INTERVAL_S * 10)

    def __enter__(self) -> Self:
        self.write_conf()
        environment = dict(os.environ)
        environment[AppConfig.APP_ROOT_KEY] = str(self.work)
        self.process = subprocess.Popen(
            [str(Path(sys.executable).parent / self.script)],
            cwd=self.work,
            env=environment,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        deadline = time.monotonic() + self.START_TIMEOUT_S
        while time.monotonic() < deadline:
            assert self.process.poll() is None, f"{self.script} stopped with code {self.process.returncode}."
            try:
                if self.get_openapi().status_code == httpx.codes.OK:
                    return self
            except httpx.TransportError:
                time.sleep(self.POLL_INTERVAL_S)
        self.__exit__(None, None, None)
        raise AssertionError(f"{self.script} did not serve within {self.START_TIMEOUT_S} seconds.")

    def __exit__(
        self,
        error_type: Optional[Type[BaseException]],
        error: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        if self.process is None:
            return
        self.process.terminate()
        try:
            self.process.wait(timeout=self.STOP_TIMEOUT_S)
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.process.wait(timeout=self.STOP_TIMEOUT_S)
        self.process = None
