from __future__ import annotations

# Standard library imports
import asyncio
from logging import Logger, getLogger
from typing import Callable, List, Optional

# Third-party imports
from nats.aio.client import Client

# First-party imports
from flight_engine.clients.leaf.squad_frame_publisher import SquadFramePublisher
from flight_engine.clients.mavlink.sample_source import SampleSource
from flight_engine.models.config.flight_engine_config import FlightEngineConfig
from flight_engine.models.missions.mission_catalog import MissionCatalog
from flight_engine.models.missions.mission_entry import MissionEntry
from flight_engine.models.telemetry.drone_state_catalog import DroneStateCatalog
from flight_engine.service.factories.missions.actors.squad_mission_actor_factory import SquadMissionActorFactory
from flight_engine.service.missions.mission_actor import MissionActor
from swarm_lifecycle.runnables.async_runnable import AsyncRunnable
from swarm_live.service.live_codec import LiveCodec
from swarm_live.service.live_hub import LiveHub
from swarm_nats.clients.nats_connector import NatsConnector


class FlightEngine(AsyncRunnable):
    """The flight engine of one edge: one asyncio process holding one actor per Mission.

    Attributes:
        config (FlightEngineConfig): The configuration of the engine.
        catalog (MissionCatalog): The Missions the engine flies.
        states (DroneStateCatalog): Maps a MAVLink ``system_status`` to the state of a Drone.
        hub (LiveHub): The hub of the local WebSocket, shared by every actor.
        codec (LiveCodec): Encodes the frames.
        source_for (Callable[[MissionEntry], SampleSource]): Gives the source of Drone samples of a Mission.
        connector (NatsConnector): Opens the connection to the leaf node.
        connection (Optional[Client]): The connection, once ``initialize`` has opened it.
        actors (List[MissionActor]): One actor per Mission.
        logger (Logger): Logger instance.

    Notes:
        - **The edge keeps flying when it loses the core**: the actors only need the local hub and the leaf node.
        - ``run`` ends when every actor has ended, or when one of them fails.
        - Each actor is run through its own ``execute``, which closes it, and ``close`` closes them again: closing a
          source twice is safe.
    """

    def __init__(
        self,
        config: FlightEngineConfig,
        catalog: MissionCatalog,
        states: DroneStateCatalog,
        hub: LiveHub,
        codec: LiveCodec,
        source_for: Callable[[MissionEntry], SampleSource],
        connector: NatsConnector,
        logger: Optional[Logger] = None,
    ) -> None:
        """Prepare the engine, not yet connected.

        Args:
            config (FlightEngineConfig): The configuration of the engine.
            catalog (MissionCatalog): The Missions to fly.
            states (DroneStateCatalog): The catalogue of Drone states.
            hub (LiveHub): The hub of the local WebSocket.
            codec (LiveCodec): The codec of the frames.
            source_for (Callable[[MissionEntry], SampleSource]): Gives the source of a Mission.
            connector (NatsConnector): The connector to the leaf node.
            logger (Optional[Logger]): Logger instance.
        """
        super().__init__(config.status_interval_s)
        self.logger = logger if logger else getLogger(__name__)
        self.config = config
        self.catalog = catalog
        self.states = states
        self.hub = hub
        self.codec = codec
        self.source_for = source_for
        self.connector = connector
        self.connection: Optional[Client] = None
        self.actors: List[MissionActor] = []

    ############################
    # Internal Helpers Methods #
    ############################

    async def _consume(self, actor: MissionActor) -> None:
        """Read every status of one actor until it ends.

        Args:
            actor (MissionActor): The actor to run.
        """
        async for status in actor.execute():
            self.logger.debug("Actor of Mission %s is %s.", actor.mission.mission_id, status)

    ############################
    # Publicly Exposed Methods #
    ############################

    async def initialize(self) -> None:
        """Connect to NATS and build one actor per Mission."""
        self.connection = await self.connector.connect()
        sink = SquadFramePublisher(self.connection)
        for mission in self.catalog.missions:
            factory = SquadMissionActorFactory(
                self.config, mission, self.states, self.source_for(mission), sink, self.hub, self.codec
            )
            self.actors.append(factory.create())
        self.logger.info("Built %d actors.", len(self.actors))

    async def run(self) -> None:
        """Run every actor concurrently until they end or the engine is cancelled."""
        if not self.actors:
            self.logger.debug("No Mission to fly.")
            return
        tasks = [asyncio.create_task(self._consume(actor)) for actor in self.actors]
        try:
            await asyncio.gather(*tasks)
        except asyncio.CancelledError:
            self.logger.debug("Cancelled the %d actors.", len(tasks))
            for task in tasks:
                task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)
            raise

    async def close(self) -> None:
        """Close every actor and disconnect. Safe after a failed or partial ``initialize``."""
        for actor in self.actors:
            await actor.close()
        if self.connection is None:
            self.logger.debug("The engine was not connected.")
            return
        connection, self.connection = self.connection, None
        await self.connector.disconnect(connection)
        self.logger.info("Closed the flight engine.")
