from __future__ import annotations

# Standard library imports
import shutil
import subprocess
from pathlib import Path
from typing import Iterator

# Third-party imports
import pytest

# First-party imports
from tests.simulator.helpers import (
    BINARY_PATH,
    BIND_ATTEMPTS,
    DOCKER_IMAGE_ENV,
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


@pytest.fixture(scope="session")
def synthetic_binary() -> Path:
    """Build the real ``swarm-synthetic-drones`` binary once and return its path."""
    if shutil.which(CARGO) is None:
        pytest.skip("cargo is not installed")
    subprocess.run(CARGO_BUILD, cwd=RUST_DIR, check=True, timeout=BUILD_TIMEOUT_S)
    return BINARY_PATH


@pytest.fixture
def simulator_script() -> Path:
    """Return the ``swarm-simulator`` console script, or skip while it is not installed."""
    path = script_path()
    if not path.exists():
        pytest.skip("swarm-simulator is not installed")
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
