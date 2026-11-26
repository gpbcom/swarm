from __future__ import annotations

# ruff: noqa: I001 -- swarm_live joins known-first-party with its package.

# Standard library imports
import asyncio
import socket
import time
from pathlib import Path
from typing import List, Optional
from uuid import UUID

# Third-party imports
from fastapi import WebSocket
from websockets.asyncio.client import connect

# First-party imports
from swarm_live.service.live_codec import LiveCodec
from swarm_models.enums import LiveOperation, LiveTopicKind
from swarm_models.live.live_subscription import LiveSubscription
from swarm_models.telemetry.squad_frame import SquadFrame

HOST = "127.0.0.1"
ENCODING = "utf-8"
OPERATOR_ID = UUID("0190a5b2-7c3e-7d4f-8a1b-2c3d4e5f6a7b")
OTHER_OPERATOR_ID = UUID("0190a5b2-7c3e-7d4f-8a1b-2c3d4e5f6a7c")
MISSION_ID = UUID("0190a5b2-7c3e-7d4f-8a1b-2c3d4e5f6a7d")
SYSTEM_IDS = list(range(1, 11))
DRONE_IDS = [UUID(f"0190a5b2-7c3e-7d4f-8a1b-{number:012x}") for number in range(0x100, 0x10A)]
OPERATOR_QUERY = "operator"
LIVE_PATH = "/v1/live"
RECEIVE_TIMEOUT_S = 15.0
SILENCE_TIMEOUT_S = 2.0
APP_TEMPLATE = (
    "tick_interval_ms: 50\n"
    "status_interval_s: 5.0\n"
    "link_lost_after_ms: 5000\n"
    'missions_catalog_path: "{missions}"\n'
    'drone_states_catalog_path: "{states}"\n'
    "nats:\n"
    '  servers: ["{nats_url}"]\n'
    "live:\n"
    "  host: 127.0.0.1\n"
    "  port: {live_port}\n"
)
MISSIONS_TEMPLATE = (
    "missions:\n"
    "  - operator_id: {operator_id}\n"
    "    mission_id: {mission_id}\n"
    "    mavlink_host: 127.0.0.1\n"
    "    mavlink_port: {mavlink_port}\n"
    "    drones:\n"
    "{drones}"
)
DRONE_TEMPLATE = "      - system_id: {system_id}\n        drone_id: {drone_id}\n"
CELL_CONFIG_TEMPLATE = (
    "server_name: cell\nhost: 127.0.0.1\nport: {port}\nleafnodes {{\n  host: 127.0.0.1\n  port: {leaf_port}\n}}\n"
)
LEAF_CONFIG_TEMPLATE = (
    "server_name: leaf\n"
    "host: 127.0.0.1\n"
    "port: {port}\n"
    'leafnodes {{\n  remotes: [ {{ url: "nats-leaf://127.0.0.1:{leaf_port}" }} ]\n}}\n'
)


def free_udp_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind((HOST, 0))
        return int(sock.getsockname()[1])


def port_accepts(port: int) -> bool:
    try:
        with socket.create_connection((HOST, port), timeout=0.2):
            return True
    except OSError:
        return False


def wait_for_port(port: int, timeout_s: float) -> bool:
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        if port_accepts(port):
            return True
        time.sleep(0.1)
    return False


def write_app_yaml(folder: Path, nats_url: str, live_port: int, missions: Path, states: Path) -> Path:
    path = folder / "app.yaml"
    path.write_text(
        APP_TEMPLATE.format(missions=missions, states=states, nats_url=nats_url, live_port=live_port),
        encoding=ENCODING,
    )
    return path


def write_missions_yaml(folder: Path, mavlink_port: int) -> Path:
    drones = "".join(
        DRONE_TEMPLATE.format(system_id=system_id, drone_id=drone_id)
        for system_id, drone_id in zip(SYSTEM_IDS, DRONE_IDS)
    )
    path = folder / "missions.yaml"
    path.write_text(
        MISSIONS_TEMPLATE.format(
            operator_id=OPERATOR_ID, mission_id=MISSION_ID, mavlink_port=mavlink_port, drones=drones
        ),
        encoding=ENCODING,
    )
    return path


def operator_from_query(websocket: WebSocket) -> UUID:
    value = websocket.query_params.get(OPERATOR_QUERY)
    if value:
        return UUID(value)
    return OPERATOR_ID


def subscription_bytes() -> bytes:
    subscription = LiveSubscription(
        op=LiveOperation.SUBSCRIBE, topic=LiveSubscription.topic_of(MISSION_ID, LiveTopicKind.SQUAD)
    )
    return LiveCodec().encode_subscription(subscription)


def live_url(port: int, operator_id: Optional[UUID] = None) -> str:
    suffix = f"?{OPERATOR_QUERY}={operator_id}" if operator_id else ""
    return f"ws://{HOST}:{port}{LIVE_PATH}{suffix}"


async def receive_full_squad(url: str) -> Optional[SquadFrame]:
    """Subscribe to the Mission and return the first SquadFrame that holds every Drone, or None on timeout."""
    codec = LiveCodec()
    async with connect(url) as client:
        await client.send(subscription_bytes())
        deadline = time.monotonic() + RECEIVE_TIMEOUT_S
        while time.monotonic() < deadline:
            try:
                data = await asyncio.wait_for(client.recv(), timeout=deadline - time.monotonic())
            except TimeoutError:
                return None
            if isinstance(data, str):
                continue
            squad = codec.decode_squad_frame(data)
            if len(squad.frames) == len(DRONE_IDS):
                return squad
    return None


async def receives_anything(url: str) -> bool:
    """Subscribe to the Mission and say whether any message arrives within the silence window."""
    async with connect(url) as client:
        await client.send(subscription_bytes())
        try:
            await asyncio.wait_for(client.recv(), timeout=SILENCE_TIMEOUT_S)
        except TimeoutError:
            return False
    return True


def drone_ids_of(squad: SquadFrame) -> List[UUID]:
    return sorted(frame.drone_id for frame in squad.frames)
