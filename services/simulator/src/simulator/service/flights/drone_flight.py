from __future__ import annotations

# Standard library imports
import time
from logging import Logger, getLogger
from typing import ClassVar, Optional
from uuid import UUID

# First-party imports
from simulator.clients.mavlink.mavlink_drone_client import MavlinkDroneClient
from simulator.models.config.flight_config import FlightConfig
from simulator.models.enums import FlightLogEntryKind
from simulator.models.flight_logs.flight_log_entry import FlightLogEntry
from simulator.models.flights.exceptions import (
    SEDroneFlightError,
    SEDroneFlightRefusedError,
    SEDroneFlightTimeoutError,
)
from simulator.models.flights.flight_outcome import FlightOutcome
from simulator.models.mavlink.exceptions import (
    SEMavlinkClientError,
    SEMavlinkClientTimeoutError,
)
from simulator.models.registry.registered_drone import RegisteredDrone
from simulator.service.routes.square_route_builder import SquareRouteBuilder
from simulator.storage.edge.flight_log_store import FlightLogStore
from swarm_lifecycle.runnables.async_runnable import AsyncRunnable


class DroneFlight(AsyncRunnable):
    """Fly one simulated Drone on a square route, and log the flight.

    Attributes:
        MICROSECONDS_PER_SECOND (int): The multiplier from seconds to microseconds.
        drone (RegisteredDrone): The Drone to fly.
        mission_id (UUID): The Mission the Flight log belongs to.
        client (MavlinkDroneClient): The client of this Drone only.
        builder (SquareRouteBuilder): Builds the route from the position of the Drone.
        store (FlightLogStore): Where the simulated Flight log is written.
        config (FlightConfig): The timings of a flight.
        outcome (Optional[FlightOutcome]): What came of the flight, once it ended.
        waypoints_reached (int): How many waypoints the Drone has reached so far.
        started_s (float): The monotonic moment the flight started.

    Notes:
        - **Every entry is simulated** (BR-014), because ``FlightLogEntry`` defaults to ``simulated=True``.
        - The store is opened and closed by the caller, such as ``SquadFlight``.
        - The Drone reports a take-off item (0), the waypoints (1 to n) and a landing item, and only the waypoints
          are logged.
    """

    MICROSECONDS_PER_SECOND: ClassVar[int] = 1_000_000

    def __init__(
        self,
        drone: RegisteredDrone,
        mission_id: UUID,
        client: MavlinkDroneClient,
        builder: SquareRouteBuilder,
        store: FlightLogStore,
        config: FlightConfig,
        logger: Optional[Logger] = None,
    ) -> None:
        """Create the flight.

        Args:
            drone (RegisteredDrone): The Drone to fly.
            mission_id (UUID): The Mission the Flight log belongs to.
            client (MavlinkDroneClient): The client of this Drone only.
            builder (SquareRouteBuilder): Builds the route from the position of the Drone.
            store (FlightLogStore): Where the simulated Flight log is written.
            config (FlightConfig): The timings of a flight, with the status interval.
            logger (Optional[Logger]): Logger instance.
        """
        super().__init__(config.status_interval_s)
        self.logger = logger if logger else getLogger(__name__)
        self.drone = drone
        self.mission_id = mission_id
        self.client = client
        self.builder = builder
        self.store = store
        self.config = config
        self.outcome: Optional[FlightOutcome] = None
        self.waypoints_reached = 0
        self.started_s = time.monotonic()

    ############################
    # Internal Helpers Methods #
    ############################

    def _record(self, kind: FlightLogEntryKind, seq: Optional[int] = None, detail: Optional[str] = None) -> None:
        """Append one simulated entry of this Drone to the Flight log.

        Args:
            kind (FlightLogEntryKind): What happened.
            seq (Optional[int]): The waypoint, when there is one.
            detail (Optional[str]): A short text, when there is one.
        """
        t_us = int(time.time() * self.MICROSECONDS_PER_SECOND)
        entry = FlightLogEntry(
            mission_id=self.mission_id, drone_id=self.drone.drone_id, t_us=t_us, kind=kind, seq=seq, detail=detail
        )
        self.store.append(entry)
        self.logger.debug("Logged %s for drone %s.", kind, self.drone.drone_id)

    def _finish(self, completed: bool) -> None:
        """Set the outcome of the flight.

        Args:
            completed (bool): Whether the Drone completed its route.
        """
        self.outcome = FlightOutcome(
            drone_id=self.drone.drone_id,
            kind=self.drone.kind,
            completed=completed,
            waypoints_reached=self.waypoints_reached,
            elapsed_s=time.monotonic() - self.started_s,
        )

    def _failure(self, error: SEMavlinkClientError) -> SEDroneFlightError:
        """Record a failed flight and build the error to raise.

        Args:
            error (SEMavlinkClientError): What the client raised.

        Returns:
            SEDroneFlightError: A timeout error for a timeout, a refused error for anything else.
        """
        self._record(FlightLogEntryKind.ROUTE_FAILED, detail=type(error).__name__)
        self._finish(False)
        self.logger.error("The flight of drone %s failed with %s.", self.drone.drone_id, type(error).__name__)
        if isinstance(error, SEMavlinkClientTimeoutError):
            return SEDroneFlightTimeoutError(f"Drone {self.drone.drone_id} did not answer in time.")
        self.logger.debug("A refusal ends the flight of drone %s.", self.drone.drone_id)
        return SEDroneFlightRefusedError(f"Drone {self.drone.drone_id} refused a command.")

    async def _fly(self) -> None:
        """Fly the route: position, upload, arm, start, then every waypoint."""
        lat_e7, lon_e7 = await self.client.position()
        route = self.builder.build(lat_e7, lon_e7)
        await self.client.upload_route(route)
        self._record(FlightLogEntryKind.ROUTE_UPLOADED)
        await self.client.arm()
        self._record(FlightLogEntryKind.ARMED)
        await self.client.start_route()
        self._record(FlightLogEntryKind.ROUTE_STARTED)
        total = len(route.waypoints)
        while self.waypoints_reached < total:
            seq = await self.client.next_reached()
            if seq < 1 or seq > total:
                self.logger.debug("Ignored item %d of drone %s.", seq, self.drone.drone_id)
                continue
            self.waypoints_reached = seq
            self._record(FlightLogEntryKind.WAYPOINT_REACHED, seq=seq)
        self._record(FlightLogEntryKind.ROUTE_COMPLETED, seq=total)
        self._finish(True)
        self.logger.info("Drone %s completed its route of %d waypoints.", self.drone.drone_id, total)

    ############################
    # Publicly Exposed Methods #
    ############################

    async def initialize(self) -> None:
        """Connect to the Drone.

        Raises:
            SEDroneFlightTimeoutError: When the Drone sends no heartbeat.
            SEDroneFlightRefusedError: When the client is refused.
        """
        self.started_s = time.monotonic()
        try:
            await self.client.connect()
        except SEMavlinkClientError as error:
            raise self._failure(error) from error

    async def run(self) -> None:
        """Fly the square route and log it.

        Raises:
            SEDroneFlightTimeoutError: When the Drone stops answering.
            SEDroneFlightRefusedError: When the Drone refuses a command.
        """
        try:
            await self._fly()
        except SEMavlinkClientError as error:
            raise self._failure(error) from error

    async def close(self) -> None:
        """Close the client of the Drone."""
        await self.client.close()
