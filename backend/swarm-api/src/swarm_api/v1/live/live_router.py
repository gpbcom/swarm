from __future__ import annotations

# Standard library imports
from logging import Logger, getLogger
from typing import Callable, ClassVar, Optional
from uuid import UUID

# Third-party imports
from fastapi import APIRouter, Depends, WebSocket

# First-party imports
from swarm_api.dependencies.live_operator import LiveOperator
from swarm_live.api.factories.live.live_session_factory import LiveSessionFactory
from swarm_live.service.live_codec import LiveCodec
from swarm_live.service.live_source import LiveSource
from swarm_models.live.session.live_session_config import LiveSessionConfig


class LiveRouter(APIRouter):
    """Serves the ``/v1/live`` WebSocket: one socket per client, many subscriptions.

    Attributes:
        PATH (ClassVar[str]): The path of the socket.
        operator (ClassVar[LiveOperator]): The dependency that tells the Operator of a connection.
        source_for (Callable[[UUID], LiveSource]): Gives the live source of one Operator.
        session_config (LiveSessionConfig): The settings of each client session.
        logger (Logger): Logger instance.

    Notes:
        - The router is built with its socket, and the gateway includes it as it is.
        - Compression is left to the WebSocket implementation of the server (permessage-deflate).
        - The handler holds no rule: the session of ``swarm_live`` does the work.
    """

    PATH: ClassVar[str] = "/v1/live"
    operator: ClassVar[LiveOperator] = LiveOperator()

    def __init__(
        self, source_for: Callable[[UUID], LiveSource], config: LiveSessionConfig, logger: Optional[Logger] = None
    ) -> None:
        """Initialise the router.

        Args:
            source_for (Callable[[UUID], LiveSource]): Gives the live source of one Operator.
            config (LiveSessionConfig): The settings of each client session.
            logger (Optional[Logger]): Logger instance.
        """
        super().__init__()
        self.logger = logger if logger else getLogger(__name__)
        self.source_for = source_for
        self.session_config = config
        self.add_api_websocket_route(self.PATH, self._serve)
        self.logger.debug("The live socket is served on %s.", self.PATH)

    ############################
    # Internal Helpers Methods #
    ############################

    async def _serve(self, websocket: WebSocket, operator_id: UUID = Depends(operator)) -> None:  # noqa: B008
        """Accept a connection and run its session until the client leaves.

        Args:
            websocket (WebSocket): The connection.
            operator_id (UUID): The Operator of the connection.
        """
        await websocket.accept()
        self.logger.debug("A live socket is accepted.")
        session = LiveSessionFactory(websocket, self.source_for(operator_id), LiveCodec(), self.session_config).create()
        async for status in session.execute():
            self.logger.debug("The live session is %s.", status)
