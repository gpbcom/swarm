from __future__ import annotations

# Standard library imports
from asyncio import DatagramTransport, get_running_loop, sleep
from logging import Logger, getLogger
from time import time_ns
from typing import ClassVar, Dict, List, Optional, Union

# Third-party imports
from swarm_core import LatestFrames

# First-party imports
from swarm_clients.flight.mavlink.mavlink_datagram_protocol import MavlinkDatagramProtocol
from swarm_clients.flight.mavlink.sample_source import SampleSource
from swarm_models.flight.clients.exceptions import SEMavlinkListenerError
from swarm_models.flight.missions.mission_entry import MissionEntry
from swarm_models.flight.telemetry.drone_sample import DroneSample


class MavlinkListener(SampleSource):
    """Receives the MAVLink frames of one Mission over UDP and keeps the latest sample of each Drone.

    Attributes:
        NS_PER_US (ClassVar[int]): The nanoseconds in a microsecond.
        mission (MissionEntry): The Mission whose host and port are listened on.
        frames (LatestFrames): The Rust store of the latest frame of each Drone.
        transport (Optional[DatagramTransport]): The UDP transport, set by ``open``.
        logger (Logger): Logger instance.

    Notes:
        - **The listener only reads**: it sends no command to any Drone, which keeps the command clause of BR-014 true.
        - A datagram that is not a well-formed frame is dropped by the Rust core.
    """

    NS_PER_US: ClassVar[int] = 1000

    def __init__(self, mission: MissionEntry, logger: Optional[Logger] = None) -> None:
        """Create the listener, not yet bound.

        Args:
            mission (MissionEntry): The Mission to listen for.
            logger (Optional[Logger]): Logger instance.
        """
        self.mission = mission
        self.frames = LatestFrames()
        self.transport: Optional[DatagramTransport] = None
        self.logger = logger if logger else getLogger(__name__)

    ############################
    # Publicly Exposed Methods #
    ############################

    def ingest(self, data: bytes) -> None:
        """Give one datagram to the Rust store, stamped with the time of arrival.

        Args:
            data (bytes): The datagram.
        """
        now_us = time_ns() // self.NS_PER_US
        count = self.frames.ingest(data, now_us)
        self.logger.debug("Ingested %d frames from a datagram of %d bytes.", count, len(data))

    def snapshot(self) -> List[DroneSample]:
        """Give the latest sample of every Drone heard from.

        Returns:
            List[DroneSample]: The samples, ordered by system id.
        """
        samples: List[DroneSample] = []
        for raw in self.frames.snapshot():
            values: Dict[str, Union[int, bool]] = {name: getattr(raw, name) for name in DroneSample.model_fields}
            samples.append(DroneSample.model_validate(values))
        return samples

    async def open(self) -> None:
        """Bind the UDP endpoint of the Mission.

        Raises:
            SEMavlinkListenerError: When the port cannot be bound.
        """
        loop = get_running_loop()
        host, port = self.mission.mavlink_host, self.mission.mavlink_port
        try:
            transport, _ = await loop.create_datagram_endpoint(
                lambda: MavlinkDatagramProtocol(self.ingest), local_addr=(host, port)
            )
        except OSError as error:
            self.logger.error("Could not bind %s:%d: %s.", host, port, type(error).__name__)
            raise SEMavlinkListenerError(
                f"Invalid port: {port!r}. The bind on {host} failed with {type(error).__name__}."
            ) from error
        self.transport = transport
        self.logger.info("Listening for MAVLink on %s:%d.", host, port)

    async def close(self) -> None:
        """Close the UDP endpoint, which frees the port. Safe to call when it was never opened."""
        if self.transport is None:
            self.logger.debug("The MAVLink listener was not open.")
            return
        self.transport.close()
        self.transport = None
        await sleep(0)
        self.logger.info("Closed the MAVLink listener.")
