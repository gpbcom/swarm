from __future__ import annotations

# Standard library imports
import time
from logging import Logger, getLogger
from typing import ClassVar, Dict, List, Optional
from uuid import UUID

# First-party imports
from simulator.clients.mavlink.mavlink_drone_client import MavlinkDroneClient
from simulator.models.commands.command_mapping_catalog import CommandMappingCatalog
from simulator.models.commands.command_reply import CommandReply
from simulator.models.commands.mavlink_command_spec import MavlinkCommandSpec
from simulator.models.config.flight_config import FlightConfig
from simulator.models.enums import CommandVerdict, FlightLogEntryKind
from simulator.models.flight_logs.flight_log_entry import FlightLogEntry
from simulator.models.mavlink.exceptions import SEMavlinkClientError
from simulator.models.registry.exceptions import SEAdapterRegistryUnknownDroneError
from simulator.models.registry.registered_drone import RegisteredDrone
from simulator.service.registry.adapter_registry import AdapterRegistry
from simulator.storage.edge.flight_log_store import FlightLogStore
from swarm_models.models.commands.command import Command


class SimulatedCommandService:
    """Carry out the commands of a Mission on the simulated Drones, and nothing else.

    Attributes:
        UNKNOWN_DRONE_REASON (str): The reason of a command to a Drone outside the adapter registry.
        UNSUPPORTED_REASON (str): The reason of a command kind the Simulator base does not support.
        DRONE_REFUSED_REASON (str): The reason when a Drone does not accept a command.
        DRONE_ERROR_REASON (str): The reason when a Drone cannot be reached or does not answer.
        NANOSECONDS_PER_MICROSECOND (int): The divisor from nanoseconds to microseconds.
        registry (AdapterRegistry): The only way to a Drone.
        store (FlightLogStore): Where the simulated Flight log is written.
        mapping (CommandMappingCatalog): The MAVLink command of each command kind.
        config (FlightConfig): The timings given to each Drone client.
        clients (Dict[UUID, MavlinkDroneClient]): The connected clients, one per Drone.
        logger (Logger): Logger instance.

    Notes:
        - **Every Drone is resolved through the adapter registry, so a command never reaches a real Drone (BR-014).**
        - A refused command is logged at ``WARNING``, written to the Flight log as simulated, and sends nothing.
    """

    UNKNOWN_DRONE_REASON: ClassVar[str] = "Drone {drone_id}: it is not in the adapter registry of the Simulator."
    UNSUPPORTED_REASON: ClassVar[str] = "Command kind {kind} is not supported by the Simulator base."
    DRONE_REFUSED_REASON: ClassVar[str] = "Drone {drone_id} did not accept the command."
    DRONE_ERROR_REASON: ClassVar[str] = "Drone {drone_id} could not carry out the command."
    NANOSECONDS_PER_MICROSECOND: ClassVar[int] = 1000

    def __init__(
        self,
        registry: AdapterRegistry,
        store: FlightLogStore,
        mapping: CommandMappingCatalog,
        config: FlightConfig,
        logger: Optional[Logger] = None,
    ) -> None:
        """Create the service.

        Args:
            registry (AdapterRegistry): The simulated Drones.
            store (FlightLogStore): The Flight log store, not yet open.
            mapping (CommandMappingCatalog): The MAVLink command of each command kind.
            config (FlightConfig): The timings given to each Drone client.
            logger (Optional[Logger]): Logger instance.
        """
        self.registry = registry
        self.store = store
        self.mapping = mapping
        self.config = config
        self.clients: Dict[UUID, MavlinkDroneClient] = {}
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

    ############################
    # Publicly Exposed Methods #
    ############################

    async def open(self) -> None:
        """Open the Flight log store."""
        self.store.open()
        self.logger.info("Opened the simulated command service.")

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

    async def close(self) -> None:
        """Close every Drone client and the store, and do nothing when already closed."""
        clients = list(self.clients.values())
        self.clients.clear()
        for client in clients:
            await client.close()
        self.store.close()
        self.logger.info("Closed the simulated command service.")
