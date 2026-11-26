from __future__ import annotations

# ruff: noqa: I001 -- swarm_live joins known-first-party with its package.

# Standard library imports
import asyncio
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import AsyncIterator, Iterator, Tuple

# Third-party imports
import pytest
import uvicorn
from fastapi import FastAPI

# First-party imports
from gateway.api.live.live_router import LiveRouter
from gateway.models.live.live_config import LiveConfig
from gateway.service.factories.live.live_feed_factory import LiveFeedFactory
from swarm_live.models.config.live_session_config import LiveSessionConfig
from swarm_nats.models.config.nats_client_config import NatsClientConfig
from tests.deploy.nats.helpers import free_port
from tests.deploy.nats.nats_server_process import NatsServerProcess
from tests.live.helpers import (
    CELL_CONFIG_TEMPLATE,
    HOST,
    LEAF_CONFIG_TEMPLATE,
    OPERATOR_ID,
    SYSTEM_IDS,
    free_udp_port,
    operator_from_query,
    wait_for_port,
    write_app_yaml,
    write_missions_yaml,
)
from tests.live.simulated_drones import SimulatedDrones

REPO_ROOT = Path(__file__).resolve().parents[2]
ENGINE_ROOT = REPO_ROOT / "services" / "flight-engine"
STATES_CATALOG = ENGINE_ROOT / "conf" / "catalogs" / "drone_states.yaml"
ENGINE_COMMAND = "swarm-flight-engine"
CONFIG_FLAG = "--config"
LOG_NAME = "engine.log"
STARTUP_TIMEOUT_S = 30.0
STOP_TIMEOUT_S = 10.0
SERVER_START_TIMEOUT_S = 15.0
FEED_READY_TIMEOUT_S = 15.0
POLL_INTERVAL_S = 0.1
PORT_PROBE_S = 0.5
DRONE_RATE_HZ = 20.0
LOG_LEVEL = "warning"


@pytest.fixture
def nats_urls(tmp_path: Path) -> Iterator[Tuple[str, str]]:
    """Run a cell and a leaf node linked to it, and give their URLs (cell, leaf)."""
    if shutil.which(NatsServerProcess.BINARY) is None:
        pytest.skip("nats-server is not installed")
    pytest.importorskip("swarm_core")
    cell_port, leaf_port, edge_port = free_port(), free_port(), free_port()
    cell = NatsServerProcess(
        tmp_path / "cell", CELL_CONFIG_TEMPLATE.format(port=cell_port, leaf_port=leaf_port), cell_port
    )
    leaf = NatsServerProcess(
        tmp_path / "leaf", LEAF_CONFIG_TEMPLATE.format(port=edge_port, leaf_port=leaf_port), edge_port
    )
    cell.spawn()
    try:
        leaf.spawn()
        yield cell.url, leaf.url
    finally:
        leaf.kill()
        cell.kill()


@pytest.fixture
def mavlink_port() -> int:
    return free_udp_port()


@pytest.fixture
def flight_engine_port(tmp_path: Path, nats_urls: Tuple[str, str], mavlink_port: int) -> Iterator[int]:
    """Run the flight engine against the leaf node and give its local live port."""
    folder = tmp_path / "engine"
    folder.mkdir()
    live_port = free_port()
    states = folder / STATES_CATALOG.name
    shutil.copy(STATES_CATALOG, states)
    missions = write_missions_yaml(folder, mavlink_port)
    app = write_app_yaml(folder, nats_urls[1], live_port, missions, states)
    log = (folder / LOG_NAME).open("wb")
    process = subprocess.Popen(
        [str(Path(sys.executable).parent / ENGINE_COMMAND), CONFIG_FLAG, str(app)],
        cwd=ENGINE_ROOT,
        stdout=log,
        stderr=log,
    )
    try:
        deadline = time.monotonic() + STARTUP_TIMEOUT_S
        while not wait_for_port(live_port, PORT_PROBE_S):
            assert process.poll() is None, (folder / LOG_NAME).read_text(errors="replace")
            assert time.monotonic() < deadline, "The flight engine did not open its live port."
        yield live_port
    finally:
        process.terminate()
        try:
            process.wait(timeout=STOP_TIMEOUT_S)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
        log.close()


@pytest.fixture
def simulated_drones(flight_engine_port: int, mavlink_port: int) -> Iterator[SimulatedDrones]:
    drones = SimulatedDrones(mavlink_port, SYSTEM_IDS, DRONE_RATE_HZ)
    drones.launch()
    yield drones
    drones.land()


@pytest.fixture
async def gateway_port(nats_urls: Tuple[str, str]) -> AsyncIterator[int]:
    """Serve the gateway's live WebSocket in this process, subscribed to the cell."""
    config = LiveConfig(nats=NatsClientConfig(servers=[nats_urls[0]]))
    feed = LiveFeedFactory(config).create()

    async def consume() -> None:
        async for _ in feed.execute():
            pass

    feed_task = asyncio.create_task(consume())
    deadline = time.monotonic() + FEED_READY_TIMEOUT_S
    ready = False
    while not ready:
        try:
            feed.source_for(OPERATOR_ID)
            ready = True
        except Exception:  # noqa: BLE001
            assert time.monotonic() < deadline, "The live feed did not become ready."
            await asyncio.sleep(POLL_INTERVAL_S)
    router = LiveRouter(feed.source_for, LiveSessionConfig())
    app = FastAPI()
    app.include_router(router.build())
    app.dependency_overrides[router.operator] = operator_from_query
    port = free_port()
    server = uvicorn.Server(uvicorn.Config(app, host=HOST, port=port, log_level=LOG_LEVEL))
    server_task = asyncio.create_task(server.serve())
    deadline = time.monotonic() + SERVER_START_TIMEOUT_S
    while not server.started:
        assert time.monotonic() < deadline, "The gateway did not start."
        await asyncio.sleep(POLL_INTERVAL_S)
    yield port
    server.should_exit = True
    await server_task
    feed_task.cancel()
    await asyncio.gather(feed_task, return_exceptions=True)
