from __future__ import annotations

# Standard library imports
import socket
import threading
from typing import ClassVar, List, Optional

# First-party imports
from tests.rust.swarm_core.helpers import (
    global_position_int_payload,
    heartbeat_payload,
    mavlink_frame,
    sys_status_payload,
)


class SimulatedDrones:
    """Simulated Drones that send MAVLink 2 frames over UDP from a background thread.

    Each Drone sends a HEARTBEAT, a SYS_STATUS and a moving GLOBAL_POSITION_INT every period.
    """

    HOST: ClassVar[str] = "127.0.0.1"
    HEARTBEAT_ID: ClassVar[int] = 0
    SYS_STATUS_ID: ClassVar[int] = 1
    GLOBAL_POSITION_INT_ID: ClassVar[int] = 33
    BASE_MODE: ClassVar[int] = 0
    SYSTEM_STATUS_ACTIVE: ClassVar[int] = 4
    BATTERY_PCT: ClassVar[int] = 80
    BASE_LAT_E7: ClassVar[int] = 473_977_000
    BASE_LON_E7: ClassVar[int] = 85_456_000
    STEP_E7: ClassVar[int] = 20
    SPACING_E7: ClassVar[int] = 100
    ALTITUDE_MM: ClassVar[int] = 50_000
    SPEED_CM_S: ClassVar[int] = 500
    HEADING_CDEG: ClassVar[int] = 9000
    SEQUENCE_MODULO: ClassVar[int] = 256
    BOOT_MS_PER_STEP: ClassVar[int] = 50
    JOIN_TIMEOUT_S: ClassVar[float] = 5.0

    def __init__(self, port: int, system_ids: List[int], rate_hz: float) -> None:
        self.port = port
        self.system_ids = system_ids
        self.rate_hz = rate_hz
        self.sent = 0
        self.stopped = threading.Event()
        self.thread: Optional[threading.Thread] = None

    ############################
    # Internal Helpers Methods #
    ############################

    def _frames_of(self, system_id: int, step: int) -> List[bytes]:
        sequence = step % self.SEQUENCE_MODULO
        lat = self.BASE_LAT_E7 + system_id * self.SPACING_E7 + step * self.STEP_E7
        lon = self.BASE_LON_E7 + system_id * self.SPACING_E7
        position = global_position_int_payload(
            lat,
            lon,
            self.ALTITUDE_MM,
            self.SPEED_CM_S,
            0,
            self.HEADING_CDEG,
            time_boot_ms=step * self.BOOT_MS_PER_STEP,
        )
        payloads = [
            (self.HEARTBEAT_ID, heartbeat_payload(self.BASE_MODE, self.SYSTEM_STATUS_ACTIVE)),
            (self.SYS_STATUS_ID, sys_status_payload(self.BATTERY_PCT)),
            (self.GLOBAL_POSITION_INT_ID, position),
        ]
        return [mavlink_frame(system_id, sequence, message_id, payload) for message_id, payload in payloads]

    def _fly(self) -> None:
        period_s = 1.0 / self.rate_hz
        step = 0
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            while not self.stopped.is_set():
                for system_id in self.system_ids:
                    for frame in self._frames_of(system_id, step):
                        sock.sendto(frame, (self.HOST, self.port))
                        self.sent += 1
                step += 1
                self.stopped.wait(period_s)

    ############################
    # Publicly Exposed Methods #
    ############################

    def launch(self) -> None:
        """Start sending frames for every Drone."""
        self.stopped.clear()
        self.thread = threading.Thread(target=self._fly, daemon=True)
        self.thread.start()

    def land(self) -> None:
        """Stop sending and wait for the thread."""
        self.stopped.set()
        if self.thread is not None:
            self.thread.join(timeout=self.JOIN_TIMEOUT_S)
            self.thread = None
