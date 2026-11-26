from __future__ import annotations

# Standard library imports
from logging import Logger, getLogger
from typing import ClassVar, Optional

# Third-party imports
from fastapi import APIRouter, WebSocket

# First-party imports
from flight_engine.models.config.live_server_config import LiveServerConfig
from swarm_live.api.factories.live.live_session_factory import LiveSessionFactory
from swarm_live.service.hub_live_source import HubLiveSource
from swarm_live.service.live_codec import LiveCodec
from swarm_live.service.live_hub import LiveHub
from swarm_models.live.session.live_session_config import LiveSessionConfig


class LiveEndpoint:
    """Serves the local ``/v1/live`` WebSocket of the flight engine, with the protocol of the gateway.

    Attributes:
        PATH (ClassVar[str]): The path of the socket.
        hub (LiveHub): The hub the Mission actors publish their frames to.
        codec (LiveCodec): Decodes the messages of the clients.
        config (LiveServerConfig): The settings of the live server.
        logger (Logger): Logger instance.

    Notes:
        - At the edge, Ground control connects straight to the flight engine, with no Operator check: the leaf node
          is local.
        - The handler holds no rule: the ``LiveSession`` of ``swarm_live`` does the work.
    """

    PATH: ClassVar[str] = "/v1/live"

    def __init__(
        self, hub: LiveHub, codec: LiveCodec, config: LiveServerConfig, logger: Optional[Logger] = None
    ) -> None:
        """Initialise the endpoint.

        Args:
            hub (LiveHub): The hub the Mission actors publish their frames to.
            codec (LiveCodec): Decodes the messages of the clients.
            config (LiveServerConfig): The settings of the live server.
            logger (Optional[Logger]): Logger instance.
        """
        self.logger = logger if logger else getLogger(__name__)
        self.hub = hub
        self.codec = codec
        self.config = config

    ############################
    # Internal Helpers Methods #
    ############################

    async def _serve(self, websocket: WebSocket) -> None:
        """Accept a connection and run its session until the client leaves.

        Args:
            websocket (WebSocket): The connection.
        """
        await websocket.accept()
        self.logger.debug("A live socket is accepted.")
        session_config = LiveSessionConfig(status_interval_s=self.config.status_interval_s)
        session = LiveSessionFactory(websocket, HubLiveSource(self.hub), self.codec, session_config).create()
        async for status in session.execute():
            self.logger.debug("The live session is %s.", status)

    ############################
    # Publicly Exposed Methods #
    ############################

    def router(self) -> APIRouter:
        """Build the router.

        Returns:
            APIRouter: A router with the live WebSocket.
        """
        router = APIRouter()
        router.add_api_websocket_route(self.PATH, self._serve)
        return router
