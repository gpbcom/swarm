from __future__ import annotations

# Standard library imports
import time
from logging import Logger, getLogger
from typing import ClassVar, Dict, List, Optional
from uuid import UUID

# First-party imports
from swarm_clients.shared.mavlink.mavlink_drone_client import MavlinkDroneClient
from swarm_models.commands.command import Command
from swarm_models.config.simulator.flight_config import FlightConfig
from swarm_models.enums import CommandVerdict, FlightLogEntryKind
from swarm_models.mavlink.exceptions import SEMavlinkClientError, SEMavlinkClientTimeoutError
from swarm_models.simulation.commands.command_mapping_catalog import CommandMappingCatalog
from swarm_models.simulation.commands.command_reply import CommandReply
from swarm_models.simulation.commands.mavlink_command_spec import MavlinkCommandSpec
from swarm_models.simulation.flight_logs.flight_log_entry import FlightLogEntry
from swarm_models.simulation.flights.exceptions import (
    SEDroneFlightError,
    SEDroneFlightRefusedError,
    SEDroneFlightTimeoutError,
)
from swarm_models.simulation.flights.flight_outcome import FlightOutcome
from swarm_models.simulation.registry.exceptions import SEAdapterRegistryUnknownDroneError
from swarm_models.simulation.registry.registered_drone import RegisteredDrone
from swarm_service.simulation.registry.adapter_registry import AdapterRegistry
from swarm_service.simulation.routes.square_route_builder import SquareRouteBuilder
from swarm_storage.simulation.flight_logs.flight_log_store import FlightLogStore


class DroneService:
    """Everything the Simulator does to its simulated Drones: carry out the commands of a Mission, and fly a route.

    Attributes:
        UNKNOWN_DRONE_REASON (str): The reason of a command to a Drone outside the adapter registry.
        UNSUPPORTED_REASON (str): The reason of a command kind the Simulator base does not support.
        DRONE_REFUSED_REASON (str): The reason when a Drone does not accept a command.
        DRONE_ERROR_REASON (str): The reason when a Drone cannot be reached or does not answer.
        NANOSECONDS_PER_MICROSECOND (int): The divisor from nanoseconds to microseconds.
        MICROSECONDS_PER_SECOND (int): The multiplier from seconds to microseconds.
        registry (AdapterRegistry): The only way to a Drone.
        store (FlightLogStore): Where the simulated Flight log is written.
        mapping (CommandMappingCatalog): The MAVLink command of each command kind.
        builder (SquareRouteBuilder): Builds the route of a flight from the position of the Drone.
        config (FlightConfig): The timings given to each Drone client.
        clients (Dict[UUID, MavlinkDroneClient]): The connected clients of the commands, one per Drone.
        outcomes (Dict[UUID, FlightOutcome]): What came of the last flight of each Drone.
        reached (Dict[UUID, int]): How many waypoints each Drone has reached in its current or last flight.
        logger (Logger): Logger instance.

    Notes:
        - **Every Drone is resolved through the adapter registry, so neither a command nor a flight ever reaches a
          real Drone (BR-014).**
        - **Every entry of the Flight log is simulated** (BR-014), because ``FlightLogEntry`` defaults to
          ``simulated=True``.
        - A refused command is logged at ``WARNING``, written to the Flight log as simulated, and sends nothing.
        - **A flight has a client of its own**, opened and closed by ``fly``, so that it never shares the link of the
          commands. The clients of the commands stay connected until ``close``.
        - During a flight, the Drone reports a take-off item (0), the waypoints (1 to n) and a landing item, and only
          the waypoints are logged.
        - This class merges the command service and the per-Drone flight of the Simulator, which handled the same
          entity in the same layer (one class per entity per layer).
    """

    UNKNOWN_DRONE_REASON: ClassVar[str] = "Drone {drone_id}: it is not in the adapter registry of the Simulator."
    UNSUPPORTED_REASON: ClassVar[str] = "Command kind {kind} is not supported by the Simulator base."
    DRONE_REFUSED_REASON: ClassVar[str] = "Drone {drone_id} did not accept the command."
    DRONE_ERROR_REASON: ClassVar[str] = "Drone {drone_id} could not carry out the command."
    NANOSECONDS_PER_MICROSECOND: ClassVar[int] = 1000
    MICROSECONDS_PER_SECOND: ClassVar[int] = 1_000_000

    def __init__(
        self,
        registry: AdapterRegistry,
        store: FlightLogStore,
        mapping: CommandMappingCatalog,
        builder: SquareRouteBuilder,
        config: FlightConfig,
        logger: Optional[Logger] = None,
    ) -> None:
        """Create the service.

        Args:
            registry (AdapterRegistry): The simulated Drones.
            store (FlightLogStore): The Flight log store, not yet open.
            mapping (CommandMappingCatalog): The MAVLink command of each command kind.
            builder (SquareRouteBuilder): Builds the route of a flight.
            config (FlightConfig): The timings given to each Drone client.
            logger (Optional[Logger]): Logger instance.
        """
        self.registry = registry
        self.store = store
        self.mapping = mapping
        self.builder = builder
        self.config = config
        self.clients: Dict[UUID, MavlinkDroneClient] = {}
        self.outcomes: Dict[UUID, FlightOutcome] = {}
        self.reached: Dict[UUID, int] = {}
        self.logger = logger if logger else getLogger(__name__)

    ############################
    # Internal Helpers Methods #
    ############################

    def _record(self, command: Command, drone_id: Optional[UUID], verdict: CommandVerdict, detail: str) -> None:
        """Write one simulated entry of the Flight log for a command.

        Args:
            command (Command): The command.
            drone_id (Optional[UUID]): The Drone concerned, or None for the whole Squad.
            verdict (CommandVerdict): Whether it was accepted or refused.
            detail (str): The text of the entry.
        """
        match verdict:
            case CommandVerdict.ACCEPTED:
                kind = FlightLogEntryKind.COMMAND_ACCEPTED
                self.logger.debug("Recording acceptance of command %s.", command.id)
            case CommandVerdict.REFUSED:
                kind = FlightLogEntryKind.COMMAND_REFUSED
                self.logger.debug("Recording refusal of command %s.", command.id)
        t_us = time.time_ns() // self.NANOSECONDS_PER_MICROSECOND
        self.store.append(
            FlightLogEntry(mission_id=command.mission_id, drone_id=drone_id, t_us=t_us, kind=kind, detail=detail)
        )

    def _refuse(self, command: Command, reason: str) -> CommandReply:
        """Refuse a command before anything is sent.

        Args:
            command (Command): The command.
            reason (str): Why it is refused, which the Flight log keeps too.

        Returns:
            CommandReply: The refused reply.
        """
        self._record(command, command.drone_id, CommandVerdict.REFUSED, reason)
        return CommandReply(command_id=command.id, verdict=CommandVerdict.REFUSED, reason=reason)

    def _targets(self, command: Command) -> List[RegisteredDrone]:
        """Resolve the Drones a command addresses.

        Args:
            command (Command): The command.

        Returns:
            List[RegisteredDrone]: The Drones, every registered one when the command names none.

        Raises:
            SEAdapterRegistryUnknownDroneError: If the named Drone is not registered.
        """
        if command.drone_id is None:
            self.logger.debug("Command %s addresses every registered Drone.", command.id)
            return self.registry.drones()
        self.logger.debug("Command %s addresses Drone %s.", command.id, command.drone_id)
        return [self.registry.resolve(command.drone_id)]

    async def _client(self, drone: RegisteredDrone) -> MavlinkDroneClient:
        """Give the connected client of a Drone, connecting it on first use.

        Args:
            drone (RegisteredDrone): The Drone.

        Returns:
            MavlinkDroneClient: The client.
        """
        cached = self.clients.get(drone.drone_id)
        if cached is not None:
            self.logger.debug("Reusing the client of Drone %s.", drone.drone_id)
            return cached
        client = MavlinkDroneClient(drone, self.config)
        await client.connect()
        self.clients[drone.drone_id] = client
        self.logger.debug("Cached the client of Drone %s.", drone.drone_id)
        return client

    async def _send(self, command: Command, drone: RegisteredDrone, spec: MavlinkCommandSpec) -> Optional[str]:
        """Send a command to one Drone and record the outcome.

        Args:
            command (Command): The command.
            drone (RegisteredDrone): The Drone.
            spec (MavlinkCommandSpec): The MAVLink command.

        Returns:
            Optional[str]: None when the Drone accepted it, otherwise the reason it did not.
        """
        try:
            client = await self._client(drone)
            accepted = await client.send_command(spec)
        except SEMavlinkClientError as error:
            self.logger.warning("Drone %s failed command %s: %s.", drone.drone_id, command.id, type(error).__name__)
            reason = self.DRONE_ERROR_REASON.format(drone_id=drone.drone_id)
            self._record(command, drone.drone_id, CommandVerdict.REFUSED, reason)
            return reason
        if accepted:
            self.logger.info("Drone %s accepted command %s.", drone.drone_id, command.id)
            self._record(command, drone.drone_id, CommandVerdict.ACCEPTED, command.kind.value)
            return None
        reason = self.DRONE_REFUSED_REASON.format(drone_id=drone.drone_id)
        self.logger.warning("Drone %s refused command %s.", drone.drone_id, command.id)
        self._record(command, drone.drone_id, CommandVerdict.REFUSED, reason)
        return reason

    def _log_flight(
        self,
        drone: RegisteredDrone,
        mission_id: UUID,
        kind: FlightLogEntryKind,
        seq: Optional[int] = None,
        detail: Optional[str] = None,
    ) -> None:
        """Append one simulated entry of a flight to the Flight log.

        Args:
            drone (RegisteredDrone): The Drone that flies.
            mission_id (UUID): The Mission the Flight log belongs to.
            kind (FlightLogEntryKind): What happened.
            seq (Optional[int]): The waypoint, when there is one.
            detail (Optional[str]): A short text, when there is one.
        """
        t_us = int(time.time() * self.MICROSECONDS_PER_SECOND)
        entry = FlightLogEntry(
            mission_id=mission_id, drone_id=drone.drone_id, t_us=t_us, kind=kind, seq=seq, detail=detail
        )
        self.store.append(entry)
        self.logger.debug("Logged %s for drone %s.", kind, drone.drone_id)

    def _finish(
        self, drone: RegisteredDrone, completed: bool, waypoints_reached: int, started_s: float
    ) -> FlightOutcome:
        """Record the outcome of a flight.

        Args:
            drone (RegisteredDrone): The Drone that flew.
            completed (bool): Whether the Drone completed its route.
            waypoints_reached (int): How many waypoints the Drone reached.
            started_s (float): The monotonic moment the flight started.

        Returns:
            FlightOutcome: The outcome, also kept in ``outcomes``.
        """
        outcome = FlightOutcome(
            drone_id=drone.drone_id,
            kind=drone.kind,
            completed=completed,
            waypoints_reached=waypoints_reached,
            elapsed_s=time.monotonic() - started_s,
        )
        self.outcomes[drone.drone_id] = outcome
        self.logger.debug("Drone %s completed its route: %s.", drone.drone_id, completed)
        return outcome

    def _flight_failure(
        self,
        drone: RegisteredDrone,
        mission_id: UUID,
        error: SEMavlinkClientError,
        waypoints_reached: int,
        started_s: float,
    ) -> SEDroneFlightError:
        """Record a failed flight and build the error to raise.

        Args:
            drone (RegisteredDrone): The Drone that flew.
            mission_id (UUID): The Mission the Flight log belongs to.
            error (SEMavlinkClientError): What the client raised.
            waypoints_reached (int): How many waypoints the Drone reached before it failed.
            started_s (float): The monotonic moment the flight started.

        Returns:
            SEDroneFlightError: A timeout error for a timeout, a refused error for anything else.
        """
        self._log_flight(drone, mission_id, FlightLogEntryKind.ROUTE_FAILED, detail=type(error).__name__)
        self._finish(drone, False, waypoints_reached, started_s)
        self.logger.error("The flight of drone %s failed with %s.", drone.drone_id, type(error).__name__)
        if isinstance(error, SEMavlinkClientTimeoutError):
            self.logger.debug("A timeout ends the flight of drone %s.", drone.drone_id)
            return SEDroneFlightTimeoutError(f"Drone {drone.drone_id} did not answer in time.")
        self.logger.debug("A refusal ends the flight of drone %s.", drone.drone_id)
        return SEDroneFlightRefusedError(f"Drone {drone.drone_id} refused a command.")

    async def _fly_route(self, drone: RegisteredDrone, mission_id: UUID, client: MavlinkDroneClient) -> int:
        """Fly the route of a connected Drone: position, upload, arm, start, then every waypoint.

        Args:
            drone (RegisteredDrone): The Drone that flies.
            mission_id (UUID): The Mission the Flight log belongs to.
            client (MavlinkDroneClient): The connected client of this flight.

        Returns:
            int: The number of waypoints of the route, all reached.

        Raises:
            SEMavlinkClientError: When the Drone stops answering or refuses a command.
        """
        lat_e7, lon_e7 = await client.position()
        route = self.builder.build(lat_e7, lon_e7)
        await client.upload_route(route)
        self._log_flight(drone, mission_id, FlightLogEntryKind.ROUTE_UPLOADED)
        await client.arm()
        self._log_flight(drone, mission_id, FlightLogEntryKind.ARMED)
        await client.start_route()
        self._log_flight(drone, mission_id, FlightLogEntryKind.ROUTE_STARTED)
        total = len(route.waypoints)
        reached = 0
        while reached < total:
            seq = await client.next_reached()
            if seq < 1 or seq > total:
                self.logger.debug("Ignored item %d of drone %s.", seq, drone.drone_id)
                continue
            reached = seq
            self.reached[drone.drone_id] = seq
            self._log_flight(drone, mission_id, FlightLogEntryKind.WAYPOINT_REACHED, seq=seq)
        self._log_flight(drone, mission_id, FlightLogEntryKind.ROUTE_COMPLETED, seq=total)
        return total

    ############################
    # Publicly Exposed Methods #
    ############################

    async def open(self) -> None:
        """Open the Flight log store."""
        self.store.open()
        self.logger.info("Opened the Drone service.")

    async def handle(self, command: Command) -> CommandReply:
        """Carry out one command on the simulated Drones.

        Args:
            command (Command): The command.

        Returns:
            CommandReply: ACCEPTED when every addressed Drone accepted it, otherwise REFUSED with the reasons.
        """
        try:
            drones = self._targets(command)
        except SEAdapterRegistryUnknownDroneError:
            reason = self.UNKNOWN_DRONE_REASON.format(drone_id=command.drone_id)
            self.logger.warning("Refused command %s to %s", command.id, reason)
            return self._refuse(command, reason)
        spec = self.mapping.commands.get(command.kind)
        if spec is None:
            reason = self.UNSUPPORTED_REASON.format(kind=command.kind.value)
            self.logger.warning("Refused command %s: %s", command.id, reason)
            return self._refuse(command, reason)
        reasons: List[str] = []
        for drone in drones:
            reason_sent = await self._send(command, drone, spec)
            if reason_sent is not None:
                reasons.append(reason_sent)
        if reasons:
            self.logger.warning("Command %s was refused by %d Drones.", command.id, len(reasons))
            return CommandReply(command_id=command.id, verdict=CommandVerdict.REFUSED, reason=" ".join(reasons))
        self.logger.info("Command %s was accepted by %d Drones.", command.id, len(drones))
        return CommandReply(command_id=command.id, verdict=CommandVerdict.ACCEPTED)

    async def fly(self, drone: RegisteredDrone, mission_id: UUID) -> FlightOutcome:
        """Fly one simulated Drone on a square route with a client of its own, and log the flight.

        Args:
            drone (RegisteredDrone): The Drone to fly, taken from the adapter registry.
            mission_id (UUID): The Mission the Flight log belongs to.

        Returns:
            FlightOutcome: The completed outcome, also kept in ``outcomes``.

        Raises:
            SEDroneFlightTimeoutError: When the Drone sends no heartbeat or stops answering.
            SEDroneFlightRefusedError: When the Drone refuses a command.

        Notes:
            - A failed flight writes ``ROUTE_FAILED`` and keeps an incomplete outcome before it raises.
            - The client of the flight is closed whatever happens.
        """
        started_s = time.monotonic()
        client = MavlinkDroneClient(self.registry.resolve(drone.drone_id), self.config)
        self.reached[drone.drone_id] = 0
        try:
            await client.connect()
            total = await self._fly_route(drone, mission_id, client)
        except SEMavlinkClientError as error:
            failure = self._flight_failure(drone, mission_id, error, self.reached[drone.drone_id], started_s)
            raise failure from error
        finally:
            await client.close()
        self.logger.info("Drone %s completed its route of %d waypoints.", drone.drone_id, total)
        return self._finish(drone, True, total, started_s)

    async def close(self) -> None:
        """Close every Drone client and the store, and do nothing when already closed."""
        clients = list(self.clients.values())
        self.clients.clear()
        for client in clients:
            await client.close()
        self.store.close()
        self.logger.info("Closed the Drone service.")
