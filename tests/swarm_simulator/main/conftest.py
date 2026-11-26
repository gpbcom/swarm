from __future__ import annotations

# Standard library imports
import shutil
import subprocess
from pathlib import Path
from typing import Iterator, Tuple

# Third-party imports
import pytest

# First-party imports
from swarm_models.enums import CredentialKind
from tests.infra.nats.helpers import free_port, issuers, operator_mode_config, write_creds
from tests.infra.nats.nats_server_process import NatsServerProcess
from tests.swarm_simulator.main.helpers import (
    BINARY_PATH,
    BIND_ATTEMPTS,
    DOCKER_IMAGE_ENV,
    OPERATOR_ID,
    PX4_CONTAINER_PORT,
    RUST_DIR,
    SYNTHETIC_COUNT,
    docker_image,
    free_udp_base_port,
    free_udp_port,
    script_path,
    start_synthetic_drones,
    stop_process,
)

CARGO = "cargo"
DOCKER = "docker"
CARGO_BUILD = [CARGO, "build", "-p", "swarm-synthetic-drones", "--locked"]
IMAGE_INSPECT = [DOCKER, "image", "inspect"]
DOCKER_RUN = [DOCKER, "run", "--rm", "-d", "-p", "{port}:{container_port}/udp", "{image}"]
DOCKER_REMOVE = [DOCKER, "rm", "-f"]
BUILD_TIMEOUT_S = 900.0
DOCKER_TIMEOUT_S = 120.0
CELL_NAME = "cell"
SIMULATED_NAME = "squad-sim"
SERVICE_NAME = "service"
CREDS_FOLDER = "creds"
JETSTREAM_FOLDER = "jetstream"

Cell = Tuple[str, int, Path, Path]


@pytest.fixture(scope="session")
def synthetic_binary() -> Path:
    """Build the real ``swarm-synthetic-drones`` binary once and return its path."""
    if shutil.which(CARGO) is None:
        pytest.skip("cargo is not installed")
    subprocess.run(CARGO_BUILD, cwd=RUST_DIR, check=True, timeout=BUILD_TIMEOUT_S)
    return BINARY_PATH


@pytest.fixture
def simulator_script() -> Path:
    """Return the ``swarm-simulator-serve`` console script, or skip while it is not installed."""
    path = script_path()
    if not path.exists():
        pytest.skip("swarm-simulator-serve is not installed")
    return path


@pytest.fixture
def synthetic_drones(synthetic_binary: Path) -> Iterator[int]:
    """Start ten synthetic Drones and yield their base port."""
    for _ in range(BIND_ATTEMPTS):
        base_port = free_udp_base_port(SYNTHETIC_COUNT)
        process = start_synthetic_drones(synthetic_binary, base_port)
        if process is not None:
            yield base_port
            stop_process(process)
            return
    raise AssertionError("swarm-synthetic-drones never became ready.")


@pytest.fixture
def px4_sitl() -> Iterator[int]:
    """Start a PX4 SITL container and yield the host UDP port of its MAVLink link."""
    if shutil.which(DOCKER) is None:
        pytest.skip("docker is not installed")
    image = docker_image()
    inspected = subprocess.run([*IMAGE_INSPECT, image], capture_output=True, check=False, timeout=DOCKER_TIMEOUT_S)
    if inspected.returncode != 0:
        pytest.skip(f"the PX4 SITL image {image} is not built, see {DOCKER_IMAGE_ENV}")
    port = free_udp_port()
    command = [part.format(port=port, container_port=PX4_CONTAINER_PORT, image=image) for part in DOCKER_RUN]
    started = subprocess.run(command, capture_output=True, text=True, check=True, timeout=DOCKER_TIMEOUT_S)
    container = started.stdout.strip()
    yield port
    subprocess.run([*DOCKER_REMOVE, container], capture_output=True, check=False, timeout=DOCKER_TIMEOUT_S)


@pytest.fixture
def nats_cell(tmp_path: Path) -> Iterator[Cell]:
    """A NATS server in operator mode with JetStream and the Operator's account, with simulated and service credentials.

    It yields the URL, the monitoring port, the simulated credentials and the service credentials: the simulator app
    stops when it cannot reach NATS, so every test that serves it needs this cell.
    """
    if shutil.which(NatsServerProcess.BINARY) is None:
        pytest.skip("nats-server is not installed")
    operator_issuer, account_issuer, credential_issuer = issuers()
    operator = operator_issuer.issue(CELL_NAME)
    account = account_issuer.issue(operator, OPERATOR_ID)
    simulated = credential_issuer.issue(account, OPERATOR_ID, CredentialKind.SIMULATED, SIMULATED_NAME)
    service = credential_issuer.issue(account, OPERATOR_ID, CredentialKind.SERVICE, SERVICE_NAME)
    simulated_creds = write_creds(tmp_path / CREDS_FOLDER, simulated, credential_issuer)
    service_creds = write_creds(tmp_path / CREDS_FOLDER, service, credential_issuer)
    port = free_port()
    monitor_port = free_port()
    config = operator_mode_config(port, monitor_port, operator, [account], store_dir=tmp_path / JETSTREAM_FOLDER)
    server = NatsServerProcess(tmp_path, config, port)
    server.spawn()
    yield server.url, monitor_port, simulated_creds, service_creds
    server.kill()
