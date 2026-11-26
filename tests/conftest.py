from __future__ import annotations

# Standard library imports
import shutil
import socket
import subprocess
import time
from pathlib import Path
from typing import AsyncIterator, Iterator

# Third-party imports
import nats
import pytest
from nats.aio.client import Client

NATS_BINARY = "nats-server"
LOCALHOST = "127.0.0.1"
NATS_URL_TEMPLATE = "nats://{host}:{port}"
START_TIMEOUT_S = 10.0
POLL_INTERVAL_S = 0.05
STOP_TIMEOUT_S = 10.0


def free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.bind((LOCALHOST, 0))
        port: int = probe.getsockname()[1]
    return port


def wait_for_port(port: int) -> bool:
    deadline = time.monotonic() + START_TIMEOUT_S
    while time.monotonic() < deadline:
        try:
            with socket.create_connection((LOCALHOST, port), timeout=POLL_INTERVAL_S):
                return True
        except OSError:
            time.sleep(POLL_INTERVAL_S)
    return False


@pytest.fixture
def nats_url(tmp_path: Path) -> Iterator[str]:
    binary = shutil.which(NATS_BINARY)
    if binary is None:
        pytest.skip("nats-server is not installed")
    port = free_port()
    process = subprocess.Popen(
        [binary, "-a", LOCALHOST, "-p", str(port), "-js", "-sd", str(tmp_path / "js")],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if not wait_for_port(port):
        process.terminate()
        process.wait(timeout=STOP_TIMEOUT_S)
        pytest.fail("nats-server did not accept connections in time")
    yield NATS_URL_TEMPLATE.format(host=LOCALHOST, port=port)
    process.terminate()
    process.wait(timeout=STOP_TIMEOUT_S)


@pytest.fixture
async def nats_client(nats_url: str) -> AsyncIterator[Client]:
    client = await nats.connect(nats_url)
    yield client
    await client.close()
