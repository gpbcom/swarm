from __future__ import annotations

# Standard library imports
from logging import Logger, getLogger
from typing import Optional

# Third-party imports
from fastapi import FastAPI

# First-party imports
from swarm_models.config.flight_engine.flight_engine_config import FlightEngineConfig
from swarm_models.flight.missions.mission_catalog import MissionCatalog
from swarm_models.flight.telemetry.drone_state_catalog import DroneStateCatalog
from swarm_service.flight.engine.flight_engine_server import FlightEngineServer
from swarm_service.flight.factories.engine.flight_engine_factory import FlightEngineFactory
from swarm_service.flight.factories.engine_factory import EngineFactory
from swarm_service.shared.live.hub.live_hub import LiveHub
from swarm_service.shared.live.live_codec import LiveCodec
from swarm_web.factories.rest_server_factory import RestServerFactory
from swarm_web.models.config.rest_config import RestConfig


class FlightEngineServerFactory(EngineFactory[FlightEngineServer]):
    """Builds the runnable of the flight engine app: the engine of an edge and the server of its live socket.

    Attributes:
        config (FlightEngineConfig): The configuration of the flight engine.
        app (FastAPI): The application that serves the live socket.
        hub (LiveHub): The hub the Mission actors publish to and the sockets read.
        codec (LiveCodec): The codec of the frames.
        logger (Logger): Logger instance.

    Notes:
        - The two catalogues are read here, in the folder of the app (``FlightEngineConfig.in_app_folder``), so that a
          relative path means the same file whatever folder the app starts in.
        - The ``live`` section of the configuration gives the host, the port and the status interval of the server.
    """

    def __init__(
        self,
        config: FlightEngineConfig,
        app: FastAPI,
        hub: LiveHub,
        codec: LiveCodec,
        logger: Optional[Logger] = None,
    ) -> None:
        """Prepare the factory.

        Args:
            config (FlightEngineConfig): The configuration of the flight engine.
            app (FastAPI): The application that serves the live socket.
            hub (LiveHub): The hub shared by the actors and the sockets.
            codec (LiveCodec): The codec of the frames.
            logger (Optional[Logger]): Logger instance.
        """
        super().__init__()
        self.logger = logger if logger else getLogger(__name__)
        self.config = config
        self.app = app
        self.hub = hub
        self.codec = codec

    ############################
    # Internal Helpers Methods #
    ############################

    def _build(self) -> FlightEngineServer:
        """Read the catalogues and build the runnable of the engine and its server.

        Returns:
            FlightEngineServer: A new runnable, not started.
        """
        catalog = MissionCatalog.load(FlightEngineConfig.in_app_folder(self.config.missions_catalog_path))
        states = DroneStateCatalog.load(FlightEngineConfig.in_app_folder(self.config.drone_states_catalog_path))
        self.logger.info("Loaded %d Missions.", len(catalog.missions))
        engine_factory = FlightEngineFactory(self.config, catalog, states, self.hub, self.codec)
        live = self.config.live
        rest = RestConfig(host=live.host, port=live.port, status_interval_s=live.status_interval_s)
        return FlightEngineServer(engine_factory, RestServerFactory(self.app, rest), self.config.status_interval_s)
