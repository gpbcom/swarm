from __future__ import annotations

import socket
import threading
import time
from types import TracebackType
from typing import ClassVar, FrozenSet, List, Optional, Self, Set, Tuple, Type

from pymavlink import mavutil


class StandInDrone:
    """A real UDP peer that answers like a Drone, for the tests of the MAVLink client."""

    LOCALHOST: ClassVar[str] = "127.0.0.1"
    DEFAULT_ACCEPTED_COMMANDS: ClassVar[FrozenSet[int]] = frozenset({20, 21, 193})
    HEARTBEAT_PERIOD_S: ClassVar[float] = 0.2
    POLL_S: ClassVar[float] = 0.02
    JOIN_S: ClassVar[float] = 2.0
    ARM_COMMAND: ClassVar[int] = 400
    START_COMMAND: ClassVar[int] = 300
    COMPONENT_ID: ClassVar[int] = 1
    BAD_DATA_TYPE: ClassVar[str] = "BAD_DATA"
    MISSION_COUNT_TYPE: ClassVar[str] = "MISSION_COUNT"
    MISSION_ITEM_TYPE: ClassVar[str] = "MISSION_ITEM_INT"
    COMMAND_TYPE: ClassVar[str] = "COMMAND_LONG"

    def __init__(
        self,
        system_id: int = 1,
        lat_e7: int = 473977420,
        lon_e7: int = 85455940,
        refuse_arm: bool = False,
        refuse_mission: bool = False,
        stall_after_seq: Optional[int] = None,
        silent: bool = False,
        step_s: float = 0.05,
    ) -> None:
        self.system_id = system_id
        self.lat_e7 = lat_e7
        self.lon_e7 = lon_e7
        self.refuse_arm = refuse_arm
        self.refuse_mission = refuse_mission
        self.stall_after_seq = stall_after_seq
        self.silent = silent
        self.step_s = step_s
        self.host = self.LOCALHOST
        self.port = self.free_port()
        self.accepted_commands: Set[int] = set(self.DEFAULT_ACCEPTED_COMMANDS)
        self.received_commands: List[int] = []
        self.uploaded_items: List[Tuple[int, int, int, int, float]] = []
        self.link: Optional[mavutil.mavfile] = None
        self.thread: Optional[threading.Thread] = None
        self.closing = threading.Event()
        self.peer_seen = False
        self.armed = False
        self.expected_count = 0
        self.next_reached_seq: Optional[int] = None
        self.next_reached_at = 0.0
        self.last_heartbeat_at = 0.0

    ############################
    # Internal Helpers Methods #
    ############################

    def free_port(self) -> int:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as probe:
            probe.bind((self.LOCALHOST, 0))
            return int(probe.getsockname()[1])

    def send_heartbeat(self, link: mavutil.mavfile) -> None:
        link.mav.heartbeat_send(
            mavutil.mavlink.MAV_TYPE_QUADROTOR,
            mavutil.mavlink.MAV_AUTOPILOT_PX4,
            0,
            0,
            mavutil.mavlink.MAV_STATE_ACTIVE,
        )
        link.mav.global_position_int_send(0, self.lat_e7, self.lon_e7, 0, 0, 0, 0, 0, 0)

    def on_mission_count(self, link: mavutil.mavfile, count: int, target_system: int) -> None:
        self.expected_count = count
        self.uploaded_items.clear()
        link.mav.mission_request_int_send(target_system, self.COMPONENT_ID, 0)

    def on_mission_item(self, link: mavutil.mavfile, item: mavutil.mavlink.MAVLink_message, target_system: int) -> None:
        self.uploaded_items.append((item.seq, item.command, item.x, item.y, item.z))
        if item.seq + 1 < self.expected_count:
            link.mav.mission_request_int_send(target_system, self.COMPONENT_ID, item.seq + 1)
            return
        verdict = mavutil.mavlink.MAV_MISSION_ACCEPTED
        if self.refuse_mission:
            verdict = mavutil.mavlink.MAV_MISSION_DENIED
            self.uploaded_items.clear()
        link.mav.mission_ack_send(target_system, self.COMPONENT_ID, verdict)

    def on_command(self, link: mavutil.mavfile, command: mavutil.mavlink.MAVLink_message) -> None:
        result = mavutil.mavlink.MAV_RESULT_ACCEPTED
        if command.command == self.ARM_COMMAND:
            if self.refuse_arm:
                return
            self.armed = True
        elif command.command == self.START_COMMAND:
            if self.armed and self.uploaded_items:
                self.next_reached_seq = 0
                self.next_reached_at = time.monotonic() + self.step_s
            else:
                result = mavutil.mavlink.MAV_RESULT_DENIED
        else:
            self.received_commands.append(command.command)
            if command.command not in self.accepted_commands:
                result = mavutil.mavlink.MAV_RESULT_UNSUPPORTED
        link.mav.command_ack_send(command.command, result)

    def advance_route(self, link: mavutil.mavfile) -> None:
        if self.next_reached_seq is None or time.monotonic() < self.next_reached_at:
            return
        if self.next_reached_seq >= len(self.uploaded_items):
            self.next_reached_seq = None
            return
        link.mav.mission_item_reached_send(self.next_reached_seq)
        if self.stall_after_seq is not None and self.next_reached_seq >= self.stall_after_seq:
            self.next_reached_seq = None
            return
        self.next_reached_seq += 1
        self.next_reached_at = time.monotonic() + self.step_s

    def handle(self, link: mavutil.mavfile, message: mavutil.mavlink.MAVLink_message) -> None:
        kind = message.get_type()
        target_system = message.get_srcSystem()
        if kind == self.MISSION_COUNT_TYPE:
            self.on_mission_count(link, message.count, target_system)
        elif kind == self.MISSION_ITEM_TYPE:
            self.on_mission_item(link, message, target_system)
        elif kind == self.COMMAND_TYPE:
            self.on_command(link, message)

    def serve_loop(self) -> None:
        link = self.link
        if link is None:
            return
        while not self.closing.is_set():
            message = link.recv_match(blocking=True, timeout=self.POLL_S)
            if message is not None and message.get_type() != self.BAD_DATA_TYPE:
                self.peer_seen = True
                if not self.silent:
                    self.handle(link, message)
            if self.silent or not self.peer_seen:
                continue
            now = time.monotonic()
            if now - self.last_heartbeat_at >= self.HEARTBEAT_PERIOD_S:
                self.last_heartbeat_at = now
                self.send_heartbeat(link)
            self.advance_route(link)

    ############################
    # Publicly Exposed Methods #
    ############################

    def __enter__(self) -> Self:
        self.link = mavutil.mavlink_connection(
            f"udpin:{self.host}:{self.port}", source_system=self.system_id, source_component=self.COMPONENT_ID
        )
        self.thread = threading.Thread(target=self.serve_loop, daemon=True)
        self.thread.start()
        return self

    def __exit__(
        self,
        error_type: Optional[Type[BaseException]],
        error: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        self.closing.set()
        if self.thread is not None:
            self.thread.join(self.JOIN_S)
            self.thread = None
        if self.link is not None:
            self.link.close()
            self.link = None
