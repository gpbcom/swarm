from __future__ import annotations

# Standard library imports
import asyncio
from logging import Logger, getLogger
from time import monotonic, time_ns
from typing import ClassVar, Optional

# First-party imports
from flight_engine.clients.leaf.frame_sink import FrameSink
from flight_engine.clients.mavlink.sample_source import SampleSource
from flight_engine.models.clients.exceptions import SESquadFramePublishError
from flight_engine.models.config.flight_engine_config import FlightEngineConfig
from flight_engine.models.missions.mission_entry import MissionEntry
from flight_engine.service.missions.squad_frame_builder import SquadFrameBuilder
from swarm_lifecycle.runnables.async_runnable import AsyncRunnable
from swarm_live.service.live_codec import LiveCodec
from swarm_live.service.live_hub import LiveHub
from swarm_models.enums import LiveTopicKind
from swarm_models.live.live_subscription import LiveSubscription


class MissionActor(AsyncRunnable):
    """Holds the Squad state of one Mission and emits one SquadFrame per tick.

    Attributes:
        config (FlightEngineConfig): The configuration of the engine.
        mission (MissionEntry): The Mission of the actor.
        source (SampleSource): Where the latest sample of each Drone comes from.
        builder (SquadFrameBuilder): Builds the SquadFrame of a tick.
        sink (FrameSink): Where the encoded frame goes, towards the leaf node.
        hub (LiveHub): The hub of the local WebSocket.
        codec (LiveCodec): Encodes the frame as MessagePack.
        ticks (int): How many ticks the actor has run.
        logger (Logger): Logger instance.
        NS_PER_US (int): The nanoseconds in a microsecond.
        MS_PER_S (float): The milliseconds in a second.

    Notes:
        - **The actor never waits for a slow Drone**: it reads the latest sample of each one and never blocks on a
          frame.
        - The ticks follow a monotonic schedule, the start plus ``n`` times the interval. A tick that took too long
          makes the actor skip the ticks it missed instead of running them in a burst.
        - The frame goes to the hub before the sink, so a slow or failing leaf node never delays the local clients.
        - A ``SESquadFramePublishError`` is logged at ``WARNING`` and the next tick still runs, because the edge keeps
          flying when it loses the core.
    """

    NS_PER_US: ClassVar[int] = 1000
    MS_PER_S: ClassVar[float] = 1000.0

    def __init__(
        self,
        config: FlightEngineConfig,
        mission: MissionEntry,
        source: SampleSource,
        builder: SquadFrameBuilder,
        sink: FrameSink,
        hub: LiveHub,
        codec: LiveCodec,
        logger: Optional[Logger] = None,
    ) -> None:
        """Prepare the actor of a Mission.

        Args:
            config (FlightEngineConfig): The configuration of the engine.
            mission (MissionEntry): The Mission.
            source (SampleSource): The source of Drone samples.
            builder (SquadFrameBuilder): The builder of SquadFrames.
            sink (FrameSink): The sink of encoded frames.
            hub (LiveHub): The hub of the local WebSocket.
            codec (LiveCodec): The codec of the frames.
            logger (Optional[Logger]): Logger instance.
        """
        super().__init__(config.status_interval_s)
        self.logger = logger if logger else getLogger(__name__)
        self.config = config
        self.mission = mission
        self.source = source
        self.builder = builder
        self.sink = sink
        self.hub = hub
        self.codec = codec
        self.ticks = 0

    ############################
    # Internal Helpers Methods #
    ############################

    async def _tick(self) -> None:
        """Run one tick: snapshot, build, encode, publish to the hub, then to the sink."""
        now_us = time_ns() // self.NS_PER_US
        frame = self.builder.build(self.source.snapshot(), now_us)
        data = self.codec.encode_squad_frame(frame)
        topic = LiveSubscription.topic_of(self.mission.mission_id, LiveTopicKind.SQUAD)
        self.hub.publish(topic, data)
        self.ticks += 1
        try:
            await self.sink.publish(self.mission.operator_id, self.mission.mission_id, data)
        except SESquadFramePublishError as error:
            self.logger.warning(
                "The sink refused the SquadFrame of Mission %s: %s.", self.mission.mission_id, type(error).__name__
            )

    ############################
    # Publicly Exposed Methods #
    ############################

    async def initialize(self) -> None:
        """Open the source of Drone samples."""
        await self.source.open()
        self.logger.debug("Opened the source of Mission %s.", self.mission.mission_id)

    async def run(self) -> None:
        """Tick every ``tick_interval_ms`` on a monotonic schedule until it is cancelled."""
        interval_s = self.config.tick_interval_ms / self.MS_PER_S
        start = monotonic()
        slot = 0
        while True:
            await self._tick()
            elapsed_slots = int((monotonic() - start) / interval_s)
            if elapsed_slots > slot:
                self.logger.debug("Skipped %d tick(s) of Mission %s.", elapsed_slots - slot, self.mission.mission_id)
            else:
                self.logger.debug("Tick %d of Mission %s was on time.", slot, self.mission.mission_id)
            slot = max(slot, elapsed_slots) + 1
            await asyncio.sleep(max(0.0, start + slot * interval_s - monotonic()))

    async def close(self) -> None:
        """Close the source. Safe when the actor never ran."""
        await self.source.close()
        self.logger.debug("Closed the source of Mission %s.", self.mission.mission_id)
