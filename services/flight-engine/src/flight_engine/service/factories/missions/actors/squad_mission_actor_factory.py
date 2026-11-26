from __future__ import annotations

# Standard library imports
from logging import Logger, getLogger
from typing import Optional

# First-party imports
from flight_engine.clients.leaf.frame_sink import FrameSink
from flight_engine.clients.mavlink.sample_source import SampleSource
from flight_engine.models.config.flight_engine_config import FlightEngineConfig
from flight_engine.models.missions.mission_entry import MissionEntry
from flight_engine.models.telemetry.drone_state_catalog import DroneStateCatalog
from flight_engine.service.factories.missions.mission_actor_factory import MissionActorFactory
from flight_engine.service.missions.mission_actor import MissionActor
from flight_engine.service.missions.squad_frame_builder import SquadFrameBuilder
from swarm_live.service.live_codec import LiveCodec
from swarm_live.service.live_hub import LiveHub


class SquadMissionActorFactory(MissionActorFactory):
    """Builds the actor of one Mission, with its own SquadFrame builder.

    Attributes:
        config (FlightEngineConfig): The configuration of the engine.
        mission (MissionEntry): The Mission of the actor.
        states (DroneStateCatalog): The catalogue of Drone states.
        source (SampleSource): The source of Drone samples.
        sink (FrameSink): The sink of encoded frames.
        hub (LiveHub): The hub of the local WebSocket.
        codec (LiveCodec): The codec of the frames.
        logger (Logger): Logger instance.
    """

    def __init__(
        self,
        config: FlightEngineConfig,
        mission: MissionEntry,
        states: DroneStateCatalog,
        source: SampleSource,
        sink: FrameSink,
        hub: LiveHub,
        codec: LiveCodec,
        logger: Optional[Logger] = None,
    ) -> None:
        """Prepare the factory.

        Args:
            config (FlightEngineConfig): The configuration of the engine.
            mission (MissionEntry): The Mission.
            states (DroneStateCatalog): The catalogue of Drone states.
            source (SampleSource): The source of Drone samples.
            sink (FrameSink): The sink of encoded frames.
            hub (LiveHub): The hub of the local WebSocket.
            codec (LiveCodec): The codec of the frames.
            logger (Optional[Logger]): Logger instance.
        """
        super().__init__()
        self.logger = logger if logger else getLogger(__name__)
        self.config = config
        self.mission = mission
        self.states = states
        self.source = source
        self.sink = sink
        self.hub = hub
        self.codec = codec

    ############################
    # Internal Helpers Methods #
    ############################

    def _build(self) -> MissionActor:
        """Build one actor, not yet opened.

        Returns:
            MissionActor: A new actor.
        """
        self.logger.debug("Building the actor of Mission %s.", self.mission.mission_id)
        builder = SquadFrameBuilder(self.mission, self.states, self.config.link_lost_after_ms)
        return MissionActor(self.config, self.mission, self.source, builder, self.sink, self.hub, self.codec)
