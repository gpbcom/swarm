from __future__ import annotations

# Standard library imports
from logging import Logger, getLogger
from typing import ClassVar, Optional
from uuid import UUID

# Third-party imports
from fastapi import WebSocket


class EdgeLiveOperator:
    """The dependency of the live socket of an edge, which accepts every local client.

    Attributes:
        EDGE (ClassVar[UUID]): The value given for every connection: the nil UUID, which names no Operator.
        logger (Logger): Logger instance.

    Notes:
        - At the edge, Ground control connects straight to the flight engine, with no Operator check: the leaf node
          is local. The flight engine serves the frames of every Mission of its edge, so its live source does not
          depend on the Operator.
    """

    EDGE: ClassVar[UUID] = UUID(int=0)

    def __init__(self, logger: Optional[Logger] = None) -> None:
        """Initialise the dependency.

        Args:
            logger (Optional[Logger]): Logger instance.
        """
        self.logger = logger if logger else getLogger(__name__)

    ############################
    # Publicly Exposed Methods #
    ############################

    async def __call__(self, websocket: WebSocket) -> UUID:
        """Accept a connection of the edge.

        Args:
            websocket (WebSocket): The connection.

        Returns:
            UUID: ``EDGE``, for every connection.
        """
        self.logger.debug("A live connection of the edge is accepted without an Operator check.")
        return self.EDGE
