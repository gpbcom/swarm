from __future__ import annotations

# Standard library imports
from logging import Logger, getLogger
from typing import Optional

# First-party imports
from swarm_clients.flight.mavlink.mavlink_listener import MavlinkListener
from swarm_models.config.flight_engine.flight_engine_config import FlightEngineConfig
from swarm_models.flight.missions.mission_catalog import MissionCatalog
from swarm_models.flight.telemetry.drone_state_catalog import DroneStateCatalog
from swarm_nats.clients.nats_connector import NatsConnector
from swarm_service.flight.engine.flight_engine import FlightEngine
from swarm_service.flight.factories.engine_factory import EngineFactory
from swarm_service.shared.live.hub.live_hub import LiveHub
from swarm_service.shared.live.live_codec import LiveCodec


class FlightEngineFactory(EngineFactory[FlightEngine]):
    """Builds the flight engine of an edge, listening for the Drones over MAVLink.

    Attributes:
        config (FlightEngineConfig): The configuration of the engine.
        catalog (MissionCatalog): The Missions to fly.
        states (DroneStateCatalog): The catalogue of Drone states.
        hub (LiveHub): The hub of the local WebSocket.
        codec (LiveCodec): The codec of the frames.
        logger (Logger): Logger instance.
    """

    def __init__(
        self,
        config: FlightEngineConfig,
        catalog: MissionCatalog,
        states: DroneStateCatalog,
        hub: LiveHub,
        codec: LiveCodec,
        logger: Optional[Logger] = None,
    ) -> None:
        """Prepare the factory.

        Args:
            config (FlightEngineConfig): The configuration of the engine.
            catalog (MissionCatalog): The Missions to fly.
            states (DroneStateCatalog): The catalogue of Drone states.
            hub (LiveHub): The hub of the local WebSocket.
            codec (LiveCodec): The codec of the frames.
            logger (Optional[Logger]): Logger instance.
        """
        super().__init__()
        self.logger = logger if logger else getLogger(__name__)
        self.config = config
        self.catalog = catalog
        self.states = states
        self.hub = hub
        self.codec = codec

    ############################
    # Internal Helpers Methods #
    ############################

    def _build(self) -> FlightEngine:
        """Build one flight engine with its own connector, not connected yet.

        Returns:
            FlightEngine: A new engine.
        """
        self.logger.debug("Building a flight engine for %d Missions.", len(self.catalog.missions))
        connector = NatsConnector(self.config.nats)
        return FlightEngine(self.config, self.catalog, self.states, self.hub, self.codec, MavlinkListener, connector)
