from __future__ import annotations

# Standard library imports
import asyncio
import os
import time
from logging import Logger, getLogger
from typing import Callable, ClassVar, List, Optional, Tuple

# Third-party imports
from pymavlink import mavutil

from simulator.models.commands.mavlink_command_spec import MavlinkCommandSpec

# First-party imports
from simulator.models.config.flight_config import FlightConfig
from simulator.models.mavlink.exceptions import SEMavlinkClientRefusedError, SEMavlinkClientTimeoutError
from simulator.models.registry.registered_drone import RegisteredDrone
from simulator.models.routes.route import Route


class MavlinkDroneClient:
    """Talks MAVLink to one registered Drone over UDP.

    Attributes:
        drone (RegisteredDrone): The only Drone this client ever connects to.
        config (FlightConfig): The timings of a flight.
        logger (Logger): Logger instance.
        link (Optional[mavutil.mavfile]): The MAVLink connection, once connected.
        GCS_SYSTEM_ID (int): The MAVLink system id this client sends from.
        TARGET_COMPONENT_ID (int): The component of the Drone that receives the messages.
        ARM_RETRY_INTERVAL_S (float): How long to wait for an arm acknowledgement before sending it again.
        GCS_HEARTBEAT_PERIOD_S (float): How often the client sends its own heartbeat while waiting for the Drone's.
        LAND_ALTITUDE_M (float): The relative altitude of the landing item.
        ENDPOINT_FORMAT (str): The format of the pymavlink connection string.
        MAVLINK2_ENV (str): The environment variable that makes pymavlink speak MAVLink 2.
        MAVLINK2_ENV_VALUE (str): The value that turns it on.
        DIALECT (str): The MAVLink dialect to load.
        HEARTBEAT_TYPE (str): The name of the heartbeat message.
        POSITION_TYPE (str): The name of the global position message.
        REQUEST_INT_TYPE (str): The name of the mission item request message.
        REQUEST_TYPE (str): The name of the legacy mission item request message.
        MISSION_ACK_TYPE (str): The name of the mission acknowledgement message.
        COMMAND_ACK_TYPE (str): The name of the command acknowledgement message.
        REACHED_TYPE (str): The name of the mission item reached message.

    Notes:
        - **The client only ever connects to the RegisteredDrone it was built with, and takes no host or port from
          anywhere else.** The adapter registry builds it from a simulated entry only, so this is how a real Drone
          stays out of reach (BR-014).
        - Every blocking ``recv_match`` runs in ``asyncio.to_thread`` with a bounded timeout, so the event loop never
          waits on the socket.
        - The MAVLink ids and enum values come from pymavlink's ``mavlink`` module, never from magic numbers.
        - **The link speaks MAVLink 2 only**: the synthetic Drones read no MAVLink 1 frame, and pymavlink sends MAVLink 1
          unless ``MAVLINK20`` is set before the dialect is loaded, so ``open_link`` sets it and reloads the dialect.
        - pymavlink is untyped, so its objects are only used through the typed methods of this class.
    """

    GCS_SYSTEM_ID: ClassVar[int] = 255
    TARGET_COMPONENT_ID: ClassVar[int] = 1
    ARM_RETRY_INTERVAL_S: ClassVar[float] = 0.5
    GCS_HEARTBEAT_PERIOD_S: ClassVar[float] = 0.5
    LAND_ALTITUDE_M: ClassVar[float] = 0.0
    ENDPOINT_FORMAT: ClassVar[str] = "udpout:{host}:{port}"
    MAVLINK2_ENV: ClassVar[str] = "MAVLINK20"
    MAVLINK2_ENV_VALUE: ClassVar[str] = "1"
    DIALECT: ClassVar[str] = "common"
    HEARTBEAT_TYPE: ClassVar[str] = "HEARTBEAT"
    POSITION_TYPE: ClassVar[str] = "GLOBAL_POSITION_INT"
    REQUEST_INT_TYPE: ClassVar[str] = "MISSION_REQUEST_INT"
    REQUEST_TYPE: ClassVar[str] = "MISSION_REQUEST"
    MISSION_ACK_TYPE: ClassVar[str] = "MISSION_ACK"
    COMMAND_ACK_TYPE: ClassVar[str] = "COMMAND_ACK"
    REACHED_TYPE: ClassVar[str] = "MISSION_ITEM_REACHED"

    def __init__(self, drone: RegisteredDrone, config: FlightConfig, logger: Optional[Logger] = None) -> None:
        """Build the client of one Drone.

        Args:
            drone (RegisteredDrone): The Drone to talk to.
            config (FlightConfig): The timings of a flight.
            logger (Optional[Logger]): Logger instance.
        """
        self.drone = drone
        self.config = config
        self.logger = logger if logger else getLogger(__name__)
        self.link: Optional[mavutil.mavfile] = None

    ############################
    # Internal Helpers Methods #
    ############################

    def open_link(self) -> mavutil.mavfile:
        """Open the UDP connection to the Drone.

        Returns:
            mavutil.mavfile: The new connection.
        """
        endpoint = self.ENDPOINT_FORMAT.format(host=self.drone.host, port=self.drone.port)
        self.logger.debug("Opening %s with MAVLink 2.", endpoint)
        os.environ[self.MAVLINK2_ENV] = self.MAVLINK2_ENV_VALUE
        mavutil.set_dialect(self.DIALECT)
        return mavutil.mavlink_connection(endpoint, source_system=self.GCS_SYSTEM_ID)

    def connected_link(self) -> mavutil.mavfile:
        """Give the open connection.

        Returns:
            mavutil.mavfile: The connection.

        Raises:
            SEMavlinkClientRefusedError: If ``connect`` was not called.
        """
        if self.link is None:
            self.logger.error("Drone %s is not connected.", self.drone.drone_id)
            raise SEMavlinkClientRefusedError(f"Drone {self.drone.drone_id} is not connected.")
        self.logger.debug("Using the link of drone %s.", self.drone.drone_id)
        return self.link

    def send_gcs_heartbeat(self, link: mavutil.mavfile) -> None:
        """Send this client's heartbeat, so that the Drone learns where to answer.

        Args:
            link (mavutil.mavfile): The connection.
        """
        link.mav.heartbeat_send(
            mavutil.mavlink.MAV_TYPE_GCS,
            mavutil.mavlink.MAV_AUTOPILOT_INVALID,
            0,
            0,
            mavutil.mavlink.MAV_STATE_ACTIVE,
        )
        self.logger.debug("Sent a heartbeat to drone %s.", self.drone.drone_id)

    def is_from_drone(self, message: mavutil.mavlink.MAVLink_message) -> bool:
        """Tell whether a message comes from the Drone of this client.

        Args:
            message (mavutil.mavlink.MAVLink_message): The message.

        Returns:
            bool: True when its source system is the Drone's.
        """
        return bool(message.get_srcSystem() == self.drone.system_id)

    def is_ack_of(self, command_id: int) -> Callable[[mavutil.mavlink.MAVLink_message], bool]:
        """Build the filter of the acknowledgements of one command.

        Args:
            command_id (int): The command id.

        Returns:
            Callable[[MAVLink_message], bool]: The filter.
        """
        self.logger.debug("Filtering the acknowledgements of command %d.", command_id)
        return lambda message: bool(message.command == command_id)

    def send_command_long(self, link: mavutil.mavfile, command_id: int, param1: float) -> None:
        """Send one ``COMMAND_LONG``.

        Args:
            link (mavutil.mavfile): The connection.
            command_id (int): The MAVLink command id.
            param1 (float): The first parameter.
        """
        link.mav.command_long_send(
            self.drone.system_id, self.TARGET_COMPONENT_ID, command_id, 0, param1, 0, 0, 0, 0, 0, 0
        )
        self.logger.debug("Sent command %d to drone %s.", command_id, self.drone.drone_id)

    async def command_result(self, link: mavutil.mavfile, command_id: int, timeout_s: float) -> int:
        """Wait for the acknowledgement of a command.

        Args:
            link (mavutil.mavfile): The connection.
            command_id (int): The MAVLink command id.
            timeout_s (float): The deadline, in seconds.

        Returns:
            int: The ``MAV_RESULT`` of the acknowledgement.

        Raises:
            SEMavlinkClientTimeoutError: If the Drone does not acknowledge in time.
        """
        message = await self.wait_for(link, [self.COMMAND_ACK_TYPE], timeout_s, self.is_ack_of(command_id))
        if message is None:
            self.logger.error("Drone %s did not acknowledge command %d.", self.drone.drone_id, command_id)
            raise SEMavlinkClientTimeoutError(f"Drone {self.drone.drone_id} did not acknowledge command {command_id}.")
        self.logger.debug("Command %d answered with result %d.", command_id, message.result)
        return int(message.result)

    def mission_items(self, route: Route) -> List[Tuple[int, int, int, int, float]]:
        """Turn a route into mission items: take off, the waypoints, land.

        Args:
            route (Route): The route.

        Returns:
            List[Tuple[int, int, int, int, float]]: Each item as sequence, command, latitude, longitude and altitude.
        """
        first, last = route.waypoints[0], route.waypoints[-1]
        items = [(0, mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, first.lat_e7, first.lon_e7, first.altitude_m)]
        for seq, waypoint in enumerate(route.waypoints, start=1):
            items.append(
                (seq, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, waypoint.lat_e7, waypoint.lon_e7, waypoint.altitude_m)
            )
        items.append(
            (len(route.waypoints) + 1, mavutil.mavlink.MAV_CMD_NAV_LAND, last.lat_e7, last.lon_e7, self.LAND_ALTITUDE_M)
        )
        self.logger.debug("Built %d mission items.", len(items))
        return items

    def send_item(self, link: mavutil.mavfile, item: Tuple[int, int, int, int, float]) -> None:
        """Send one mission item.

        Args:
            link (mavutil.mavfile): The connection.
            item (Tuple[int, int, int, int, float]): Sequence, command, latitude, longitude and altitude.
        """
        seq, command, lat_e7, lon_e7, altitude_m = item
        link.mav.mission_item_int_send(
            self.drone.system_id,
            self.TARGET_COMPONENT_ID,
            seq,
            mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT,
            command,
            0,
            1,
            0,
            0,
            0,
            0,
            lat_e7,
            lon_e7,
            altitude_m,
        )
        self.logger.debug("Sent mission item %d.", seq)

    async def wait_for(
        self,
        link: mavutil.mavfile,
        types: List[str],
        timeout_s: float,
        accept: Optional[Callable[[mavutil.mavlink.MAVLink_message], bool]] = None,
    ) -> Optional[mavutil.mavlink.MAVLink_message]:
        """Wait for the next accepted message of the Drone, within a deadline.

        Args:
            link (mavutil.mavfile): The connection.
            types (List[str]): The names of the message types to wait for.
            timeout_s (float): The deadline, in seconds.
            accept (Optional[Callable[[MAVLink_message], bool]]): A further filter on the message.

        Returns:
            Optional[mavutil.mavlink.MAVLink_message]: The message, or None when the deadline passed.
        """
        deadline = time.monotonic() + timeout_s
        while True:
            remaining_s = deadline - time.monotonic()
            if remaining_s <= 0:
                self.logger.debug("Deadline passed waiting for %s.", types)
                return None
            message = await asyncio.to_thread(link.recv_match, type=types, blocking=True, timeout=remaining_s)
            if message is None:
                self.logger.debug("Nothing received for %s.", types)
                continue
            if not self.is_from_drone(message):
                self.logger.debug("Skipped a message of another system.")
                continue
            if accept is not None and not accept(message):
                self.logger.debug("Skipped a message that was not accepted.")
                continue
            self.logger.debug("Received %s.", message.get_type())
            return message

    ############################
    # Publicly Exposed Methods #
    ############################

    async def connect(self) -> None:
        """Open the link and wait for the heartbeat of the Drone.

        Raises:
            SEMavlinkClientTimeoutError: If no heartbeat comes within ``heartbeat_timeout_s``.
        """
        link = await asyncio.to_thread(self.open_link)
        self.link = link
        deadline = time.monotonic() + self.config.heartbeat_timeout_s
        while True:
            remaining_s = deadline - time.monotonic()
            if remaining_s <= 0:
                self.logger.error("Drone %s sent no heartbeat.", self.drone.drone_id)
                raise SEMavlinkClientTimeoutError(f"Drone {self.drone.drone_id} sent no heartbeat.")
            self.send_gcs_heartbeat(link)
            wait_s = min(self.GCS_HEARTBEAT_PERIOD_S, remaining_s)
            message = await self.wait_for(link, [self.HEARTBEAT_TYPE], wait_s)
            if message is not None:
                self.logger.info("Connected to drone %s.", self.drone.drone_id)
                return
            self.logger.debug("No heartbeat yet from drone %s.", self.drone.drone_id)

    async def position(self) -> Tuple[int, int]:
        """Read the position of the Drone.

        Returns:
            Tuple[int, int]: Latitude and longitude, in degrees multiplied by 1e7.

        Raises:
            SEMavlinkClientTimeoutError: If no position comes within ``heartbeat_timeout_s``.
        """
        link = self.connected_link()
        message = await self.wait_for(link, [self.POSITION_TYPE], self.config.heartbeat_timeout_s)
        if message is None:
            self.logger.error("Drone %s sent no position.", self.drone.drone_id)
            raise SEMavlinkClientTimeoutError(f"Drone {self.drone.drone_id} sent no position.")
        self.logger.debug("Drone %s is at %d, %d.", self.drone.drone_id, message.lat, message.lon)
        return int(message.lat), int(message.lon)

    async def upload_route(self, route: Route) -> None:
        """Upload a route as a mission and wait for the Drone to accept it.

        Args:
            route (Route): The route.

        Raises:
            SEMavlinkClientTimeoutError: If the Drone stops answering.
            SEMavlinkClientRefusedError: If the Drone refuses the mission.
        """
        link = self.connected_link()
        items = self.mission_items(route)
        link.mav.mission_count_send(self.drone.system_id, self.TARGET_COMPONENT_ID, len(items))
        self.logger.info("Uploading %d mission items to drone %s.", len(items), self.drone.drone_id)
        types = [self.REQUEST_INT_TYPE, self.REQUEST_TYPE, self.MISSION_ACK_TYPE]
        while True:
            message = await self.wait_for(link, types, self.config.heartbeat_timeout_s)
            if message is None:
                self.logger.error("Drone %s stopped answering the upload.", self.drone.drone_id)
                raise SEMavlinkClientTimeoutError(f"Drone {self.drone.drone_id} stopped answering the upload.")
            if message.get_type() == self.MISSION_ACK_TYPE:
                if message.type == mavutil.mavlink.MAV_MISSION_ACCEPTED:
                    self.logger.info("Drone %s accepted the mission.", self.drone.drone_id)
                    return
                self.logger.error("Drone %s refused the mission with %d.", self.drone.drone_id, message.type)
                raise SEMavlinkClientRefusedError(f"Drone {self.drone.drone_id} refused the mission.")
            if not 0 <= message.seq < len(items):
                self.logger.error("Drone %s asked for item %d.", self.drone.drone_id, message.seq)
                raise SEMavlinkClientRefusedError(f"Drone {self.drone.drone_id} asked for an unknown item.")
            self.send_item(link, items[message.seq])

    async def arm(self) -> None:
        """Arm the Drone, sending the command again until it accepts or ``arm_timeout_s`` passes.

        Raises:
            SEMavlinkClientTimeoutError: If the Drone does not accept the command in time.
        """
        link = self.connected_link()
        command_id = mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM
        deadline = time.monotonic() + self.config.arm_timeout_s
        attempt = 0
        while True:
            remaining_s = deadline - time.monotonic()
            if remaining_s <= 0:
                self.logger.error("Drone %s did not arm in time.", self.drone.drone_id)
                raise SEMavlinkClientTimeoutError(f"Drone {self.drone.drone_id} did not arm in time.")
            if attempt > 0:
                self.logger.warning("Retrying to arm drone %s, attempt %d.", self.drone.drone_id, attempt + 1)
            attempt += 1
            self.send_command_long(link, command_id, 1.0)
            wait_s = min(self.ARM_RETRY_INTERVAL_S, remaining_s)
            message = await self.wait_for(link, [self.COMMAND_ACK_TYPE], wait_s, self.is_ack_of(command_id))
            if message is None:
                self.logger.debug("No arm acknowledgement from drone %s.", self.drone.drone_id)
                continue
            if message.result == mavutil.mavlink.MAV_RESULT_ACCEPTED:
                self.logger.info("Armed drone %s.", self.drone.drone_id)
                return
            self.logger.debug("Drone %s answered the arm command with %d.", self.drone.drone_id, message.result)
            await asyncio.sleep(max(0.0, min(self.ARM_RETRY_INTERVAL_S, deadline - time.monotonic())))

    async def start_route(self) -> None:
        """Start the uploaded mission.

        Raises:
            SEMavlinkClientTimeoutError: If the Drone does not answer.
            SEMavlinkClientRefusedError: If the Drone refuses to start.
        """
        link = self.connected_link()
        command_id = mavutil.mavlink.MAV_CMD_MISSION_START
        self.send_command_long(link, command_id, 0.0)
        result = await self.command_result(link, command_id, self.config.heartbeat_timeout_s)
        if result != mavutil.mavlink.MAV_RESULT_ACCEPTED:
            self.logger.error("Drone %s refused to start the route with %d.", self.drone.drone_id, result)
            raise SEMavlinkClientRefusedError(f"Drone {self.drone.drone_id} refused to start the route.")
        self.logger.info("Started the route of drone %s.", self.drone.drone_id)

    async def next_reached(self) -> int:
        """Wait for the next mission item the Drone reaches.

        Returns:
            int: The sequence number of the item.

        Raises:
            SEMavlinkClientTimeoutError: If none is reached within ``route_timeout_s``.
        """
        link = self.connected_link()
        message = await self.wait_for(link, [self.REACHED_TYPE], self.config.route_timeout_s)
        if message is None:
            self.logger.error("Drone %s reached no further item.", self.drone.drone_id)
            raise SEMavlinkClientTimeoutError(f"Drone {self.drone.drone_id} reached no further item.")
        self.logger.debug("Drone %s reached item %d.", self.drone.drone_id, message.seq)
        return int(message.seq)

    async def send_command(self, spec: MavlinkCommandSpec) -> bool:
        """Send one command and wait for its verdict.

        Args:
            spec (MavlinkCommandSpec): The command.

        Returns:
            bool: True when the Drone accepted it, False when it refused or does not support it.

        Raises:
            SEMavlinkClientTimeoutError: If the Drone does not answer.
        """
        link = self.connected_link()
        self.send_command_long(link, spec.command_id, spec.param1)
        result = await self.command_result(link, spec.command_id, self.config.heartbeat_timeout_s)
        if result == mavutil.mavlink.MAV_RESULT_ACCEPTED:
            self.logger.info("Drone %s accepted command %d.", self.drone.drone_id, spec.command_id)
            return True
        self.logger.info("Drone %s did not accept command %d.", self.drone.drone_id, spec.command_id)
        return False

    async def close(self) -> None:
        """Close the link, and do nothing when it is already closed."""
        link = self.link
        if link is None:
            self.logger.debug("Link of drone %s already closed.", self.drone.drone_id)
            return
        self.link = None
        await asyncio.to_thread(link.close)
        self.logger.debug("Closed the link of drone %s.", self.drone.drone_id)
