from __future__ import annotations

# Standard library imports
import asyncio
import socket
from typing import AsyncIterator, Callable, List
from uuid import UUID, uuid4

# Third-party imports
import pytest

# First-party imports
from flight_engine.clients.mavlink.mavlink_listener import MavlinkListener  # isort: skip
from flight_engine.models.clients.exceptions import SEMavlinkListenerError  # isort: skip
from flight_engine.models.missions.mission_entry import MissionEntry  # isort: skip
from flight_engine.models.telemetry.drone_sample import DroneSample  # isort: skip
from tests.rust.swarm_core.helpers import (  # isort: skip
    global_position_int_payload,
    heartbeat_payload,
    mavlink_frame,
    sys_status_payload,
)

pytest.importorskip("swarm_core")

LOCALHOST = "127.0.0.1"
HEARTBEAT_ID = 0
SYS_STATUS_ID = 1
GLOBAL_POSITION_INT_ID = 33
WAIT_S = 5.0
SETTLE_S = 0.2
POLL_S = 0.02
LAT_E7 = 473977420
LON_E7 = 85455940
ALT_MM = 12000
VX = 150
VY = -20
HDG = 9000
BATTERY = 76
BASE_MODE = 209
SYSTEM_STATUS = 4


def a_uuid7() -> UUID:
    raw = bytearray(uuid4().bytes)
    raw[6] = (raw[6] & 0x0F) | 0x70
    raw[8] = (raw[8] & 0x3F) | 0x80
    return UUID(bytes=bytes(raw))


def a_mission(port: int) -> MissionEntry:
    return MissionEntry(
        operator_id=a_uuid7(),
        mission_id=a_uuid7(),
        mavlink_host=LOCALHOST,
        mavlink_port=port,
        drones=[],
    )


def frames_of(system_id: int) -> List[bytes]:
    return [
        mavlink_frame(system_id, 1, HEARTBEAT_ID, heartbeat_payload(BASE_MODE, SYSTEM_STATUS)),
        mavlink_frame(system_id, 2, SYS_STATUS_ID, sys_status_payload(BATTERY)),
        mavlink_frame(
            system_id,
            3,
            GLOBAL_POSITION_INT_ID,
            global_position_int_payload(LAT_E7, LON_E7, ALT_MM, VX, VY, HDG),
        ),
    ]


def send(port: int, datagrams: List[bytes]) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sender:
        for datagram in datagrams:
            sender.sendto(datagram, (LOCALHOST, port))


async def wait_until(listener: MavlinkListener, accept: Callable[[List[DroneSample]], bool]) -> List[DroneSample]:
    deadline = asyncio.get_running_loop().time() + WAIT_S
    samples = listener.snapshot()
    while not accept(samples) and asyncio.get_running_loop().time() < deadline:
        await asyncio.sleep(POLL_S)
        samples = listener.snapshot()
    return samples


class TestMavlinkListener:
    @pytest.fixture
    async def listener(self, free_udp_port: int) -> AsyncIterator[MavlinkListener]:
        listener = MavlinkListener(a_mission(free_udp_port))
        await listener.open()
        yield listener
        await listener.close()

    async def test_frames_sent_over_udp_show_up_in_the_snapshot(
        self, listener: MavlinkListener, free_udp_port: int
    ) -> None:
        send(free_udp_port, frames_of(1))
        samples = await wait_until(listener, lambda found: bool(found) and found[0].has_position)
        assert len(samples) == 1
        sample = samples[0]
        assert sample.system_id == 1
        assert sample.has_position
        assert sample.lat_e7 == LAT_E7
        assert sample.lon_e7 == LON_E7
        assert sample.relative_alt_mm == ALT_MM
        assert sample.vx_cm_s == VX
        assert sample.vy_cm_s == VY
        assert sample.hdg_cdeg == HDG
        assert sample.battery_remaining == BATTERY
        assert sample.base_mode == BASE_MODE
        assert sample.system_status == SYSTEM_STATUS
        assert sample.received >= 3

    async def test_two_drones_give_two_samples(self, listener: MavlinkListener, free_udp_port: int) -> None:
        send(free_udp_port, frames_of(1) + frames_of(2))
        samples = await wait_until(listener, lambda found: len(found) >= 2 and all(s.has_position for s in found))
        assert sorted(sample.system_id for sample in samples) == [1, 2]

    async def test_a_corrupted_datagram_is_ignored(self, listener: MavlinkListener, free_udp_port: int) -> None:
        good = frames_of(1)[0]
        corrupted = good[:-1] + bytes([good[-1] ^ 0xFF])
        send(free_udp_port, [corrupted, b"not a mavlink frame"])
        await asyncio.sleep(SETTLE_S)
        assert listener.snapshot() == []
        send(free_udp_port, [good])
        samples = await wait_until(listener, bool)
        assert [sample.system_id for sample in samples] == [1]

    async def test_a_port_already_in_use_is_refused(self, free_udp_port: int) -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as holder:
            holder.bind((LOCALHOST, free_udp_port))
            listener = MavlinkListener(a_mission(free_udp_port))
            with pytest.raises(SEMavlinkListenerError):
                await listener.open()
            await listener.close()

    async def test_close_frees_the_port(self, free_udp_port: int) -> None:
        listener = MavlinkListener(a_mission(free_udp_port))
        await listener.open()
        await listener.close()
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as probe:
            probe.bind((LOCALHOST, free_udp_port))
