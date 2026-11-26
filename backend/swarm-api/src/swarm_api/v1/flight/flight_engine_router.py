from __future__ import annotations

# Standard library imports
from logging import Logger, getLogger
from typing import ClassVar, Optional
from uuid import UUID

# Third-party imports
from fastapi import APIRouter, FastAPI

# First-party imports
from swarm_api.dependencies.edge_live_operator import EdgeLiveOperator
from swarm_api.handlers.problem_handlers import ProblemHandlers
from swarm_api.v1.live.live_router import LiveRouter
from swarm_models.config.flight_engine.flight_engine_config import FlightEngineConfig
from swarm_models.live.session.live_session_config import LiveSessionConfig
from swarm_service.shared.live.hub.live_hub import LiveHub
from swarm_service.shared.live.live_codec import LiveCodec
from swarm_service.shared.live.sources.hub_live_source import HubLiveSource
from swarm_service.shared.live.sources.live_source import LiveSource


class FlightEngineRouter(APIRouter):
    """The ``/v1`` routes of the flight domain, and the FastAPI application of the flight engine app that serves them.

    Attributes:
        TITLE (ClassVar[str]): The title of the API.
        VERSION (ClassVar[str]): The version of the API.
        flight_engine_config (FlightEngineConfig): The configuration of the flight engine.
        hub (LiveHub): The hub the Mission actors publish their frames to, which the live socket reads.
        codec (LiveCodec): The codec shared by the actors and the sockets.
        logger (Logger): Logger instance.

    Notes:
        - The domain has no REST route: its application serves the local ``/v1/live`` WebSocket, with the
          ``LiveRouter`` the gateway serves too, and the protocol of the gateway.
        - **At the edge there is no Operator check**: ``EdgeLiveOperator`` accepts every local client, and every
          client reads the hub of the edge.
        - The hub and the codec are created here and handed by the app to the runnable of the engine, so that the
          actors and the sockets share them.
    """

    TITLE: ClassVar[str] = "Swarm flight engine"
    VERSION: ClassVar[str] = "0.1.0"

    def __init__(self, config: FlightEngineConfig, logger: Optional[Logger] = None) -> None:
        """Initialise the router, with its hub and its codec.

        Args:
            config (FlightEngineConfig): The configuration of the flight engine.
            logger (Optional[Logger]): Logger instance.
        """
        super().__init__()
        self.logger = logger if logger else getLogger(__name__)
        self.flight_engine_config = config
        self.hub = LiveHub()
        self.codec = LiveCodec()

    ############################
    # Internal Helpers Methods #
    ############################

    def _source_for(self, operator_id: UUID) -> LiveSource:
        """Give the live source of a connection of the edge.

        Args:
            operator_id (UUID): The value of ``EdgeLiveOperator``, which names no Operator.

        Returns:
            LiveSource: A source that reads the hub of the edge.
        """
        self.logger.debug("A live client of the edge reads its hub.")
        return HubLiveSource(self.hub)

    ############################
    # Publicly Exposed Methods #
    ############################

    def application(self) -> FastAPI:
        """Build the application of the flight engine app.

        Returns:
            FastAPI: The application, with the REST conventions of Swarm and the local live socket.
        """
        self.logger.debug("Building the flight engine application.")
        app = ProblemHandlers().application(self.TITLE, self.VERSION, [self])
        session = LiveSessionConfig(status_interval_s=self.flight_engine_config.live.status_interval_s)
        app.include_router(LiveRouter(self._source_for, session, EdgeLiveOperator()))
        self.logger.debug("The live socket of the edge is wired on the flight engine application.")
        return app
