from __future__ import annotations

# Standard library imports
from logging import Logger, getLogger
from typing import Awaitable, Callable, ClassVar, Optional
from uuid import UUID

# Third-party imports
from fastapi import APIRouter, WebSocket

# First-party imports
from swarm_api.dependencies.live_operator import LiveOperator
from swarm_models.live.session.live_session_config import LiveSessionConfig
from swarm_service.shared.live.factories.live.live_session_factory import LiveSessionFactory
from swarm_service.shared.live.live_codec import LiveCodec
from swarm_service.shared.live.sources.live_source import LiveSource


class LiveRouter(APIRouter):
    """Serves the ``/v1/live`` WebSocket: one socket per client, many subscriptions.

    Attributes:
        PATH (ClassVar[str]): The path of the socket.
        source_for (Callable[[UUID], LiveSource]): Gives the live source of one Operator.
        session_config (LiveSessionConfig): The settings of each client session.
        operator (Callable[[WebSocket], Awaitable[UUID]]): Tells the Operator of a connection, or refuses it.
        logger (Logger): Logger instance.

    Notes:
        - The router is built with its socket, and each app includes it as it is: the gateway, whose ``LiveOperator``
          verifies the token, and the flight engine of an edge, whose ``EdgeLiveOperator`` accepts its local clients.
        - **The Operator is found before the socket is accepted**, so a refused connection is closed with the code
          its dependency gives.
        - Compression is left to the WebSocket implementation of the server (permessage-deflate).
        - The handler holds no rule: the ``LiveSession`` of the service layer does the work.
    """

    PATH: ClassVar[str] = "/v1/live"

    def __init__(
        self,
        source_for: Callable[[UUID], LiveSource],
        config: LiveSessionConfig,
        operator: Optional[Callable[[WebSocket], Awaitable[UUID]]] = None,
        logger: Optional[Logger] = None,
    ) -> None:
        """Initialise the router.

        Args:
            source_for (Callable[[UUID], LiveSource]): Gives the live source of one Operator.
            config (LiveSessionConfig): The settings of each client session.
            operator (Optional[Callable[[WebSocket], Awaitable[UUID]]]): Tells the Operator of a connection. The
                gateway's ``LiveOperator`` when it is ``None``.
            logger (Optional[Logger]): Logger instance.
        """
        super().__init__()
        self.logger = logger if logger else getLogger(__name__)
        self.source_for = source_for
        self.session_config = config
        if operator is None:
            self.logger.debug("The Operator of a connection comes from its verified token.")
            self.operator: Callable[[WebSocket], Awaitable[UUID]] = LiveOperator()
        else:
            self.logger.debug("The Operator of a connection comes from the dependency given.")
            self.operator = operator
        self.add_api_websocket_route(self.PATH, self._serve)
        self.logger.debug("The live socket is served on %s.", self.PATH)

    ############################
    # Internal Helpers Methods #
    ############################

    async def _serve(self, websocket: WebSocket) -> None:
        """Find the Operator of a connection, accept it and run its session until the client leaves.

        Args:
            websocket (WebSocket): The connection.
        """
        operator_id = await self.operator(websocket)
        await websocket.accept()
        self.logger.debug("A live socket is accepted.")
        session = LiveSessionFactory(websocket, self.source_for(operator_id), LiveCodec(), self.session_config).create()
        async for status in session.execute():
            self.logger.debug("The live session is %s.", status)
