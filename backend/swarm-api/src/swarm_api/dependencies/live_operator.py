from __future__ import annotations

# Standard library imports
from logging import Logger, getLogger
from typing import ClassVar, List, Optional
from uuid import UUID

# Third-party imports
from fastapi import WebSocket, WebSocketException

# First-party imports
from gateway.api.rest.auth.access_installer import AccessInstaller
from gateway.api.rest.auth.route_access import RouteAccess
from gateway.models.access.exceptions import SEAccessError
from gateway.service.auth.access_service import AccessService
from swarm_models.people.enums import RoleName


class LiveOperator:
    """The dependency of the live socket that tells which Operator a connection belongs to.

    Attributes:
        POLICY_VIOLATION (ClassVar[int]): The close code of a connection that has no verified Operator.
        ROLES (ClassVar[List[RoleName]]): The roles that may open a live socket: every role that belongs to an Operator.
        logger (Logger): Logger instance.

    Notes:
        - **The Operator comes from the verified token only**, checked by the access service the gateway installed on
          the application, never from a message of the client (BR-008).
        - A Swarm administrator has no Operator, so it never opens a live socket.
    """

    POLICY_VIOLATION: ClassVar[int] = 1008
    ROLES: ClassVar[List[RoleName]] = [role for role in RoleName if role != RoleName.SWARM_ADMINISTRATOR]

    def __init__(self, logger: Optional[Logger] = None) -> None:
        """Initialise the dependency.

        Args:
            logger (Optional[Logger]): Logger instance.
        """
        self.logger = logger if logger else getLogger(__name__)

    ############################
    # Internal Helpers Methods #
    ############################

    def _token(self, websocket: WebSocket) -> Optional[str]:
        """Read the bearer token of the handshake.

        Args:
            websocket (WebSocket): The connection.

        Returns:
            Optional[str]: The token without its scheme, none when there is none.
        """
        header = websocket.headers.get(RouteAccess.AUTHORIZATION)
        if header is None:
            self.logger.debug("The connection has no authorisation header.")
            return None
        parts = header.split(None, 1)
        if len(parts) != 2 or parts[0].casefold() != RouteAccess.BEARER.casefold():
            self.logger.debug("The authorisation header of the connection is not a bearer token.")
            return None
        return parts[1].strip()

    ############################
    # Publicly Exposed Methods #
    ############################

    async def __call__(self, websocket: WebSocket) -> UUID:
        """Verify the connection and give its Operator.

        Args:
            websocket (WebSocket): The connection.

        Returns:
            UUID: The Operator of the verified caller.

        Raises:
            WebSocketException: With code 1008 if the connection carries no verified Operator.
        """
        service: Optional[AccessService] = getattr(websocket.app.state, AccessInstaller.ACCESS_SERVICE_STATE, None)
        if service is None:
            self.logger.warning("A live connection was refused: no access check is installed.")
            raise WebSocketException(code=self.POLICY_VIOLATION)
        try:
            caller = await service.authorise(self._token(websocket), self.ROLES, None)
        except SEAccessError as error:
            self.logger.warning("A live connection was refused: %s.", type(error).__name__)
            raise WebSocketException(code=self.POLICY_VIOLATION) from error
        if caller.operator_id is None:
            self.logger.warning("A live connection was refused: the caller has no Operator.")
            raise WebSocketException(code=self.POLICY_VIOLATION)
        self.logger.debug("A live connection is authorised.")
        return caller.operator_id
