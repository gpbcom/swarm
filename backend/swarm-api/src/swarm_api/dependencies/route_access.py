from __future__ import annotations

# Standard library imports
from logging import Logger, getLogger
from typing import ClassVar, List, Optional
from uuid import UUID

# Third-party imports
from fastapi import Request

# First-party imports
from swarm_api.handlers.access_handlers import AccessHandlers
from swarm_models.access.exceptions import SEAccessWrongOperatorError
from swarm_models.auth.caller import Caller
from swarm_models.people.enums import RoleName
from swarm_service.gateway.auth.access_service import AccessService


class RouteAccess:
    """The dependency of a route that checks the token, the role and the Operator of a call.

    Attributes:
        AUTHORIZATION (ClassVar[str]): The name of the header that carries the token.
        BEARER (ClassVar[str]): The scheme of the token.
        OPERATOR_PARAMETER (ClassVar[str]): The name of the path parameter that names the Operator.
        roles (List[RoleName]): The roles that may make the call.
        logger (Logger): Logger instance.

    Notes:
        - **The token is never logged.**
        - A scheme other than ``Bearer`` counts as no token.
    """

    AUTHORIZATION: ClassVar[str] = "Authorization"
    BEARER: ClassVar[str] = "Bearer"
    OPERATOR_PARAMETER: ClassVar[str] = "operator_id"

    def __init__(self, roles: List[RoleName], logger: Optional[Logger] = None) -> None:
        """Initialise the dependency.

        Args:
            roles (List[RoleName]): The roles that may make the call.
            logger (Optional[Logger]): Logger instance.
        """
        self.roles = roles
        self.logger = logger if logger else getLogger(__name__)

    ############################
    # Internal Helpers Methods #
    ############################

    def _token(self, request: Request) -> Optional[str]:
        """Read the bearer token of a request.

        Args:
            request (Request): The request.

        Returns:
            Optional[str]: The token without its scheme, none when there is none.
        """
        header = request.headers.get(self.AUTHORIZATION)
        if header is None:
            self.logger.debug("The call has no authorisation header.")
            return None
        parts = header.split(None, 1)
        if len(parts) != 2 or parts[0].casefold() != self.BEARER.casefold():
            self.logger.debug("The authorisation header is not a bearer token.")
            return None
        return parts[1].strip()

    def _operator_id(self, request: Request) -> Optional[UUID]:
        """Read the Operator a call names in its path.

        Args:
            request (Request): The request.

        Returns:
            Optional[UUID]: The Operator, none when the path names none.

        Raises:
            SEAccessWrongOperatorError: If the identifier is not a UUID.
        """
        raw = request.path_params.get(self.OPERATOR_PARAMETER)
        if raw is None:
            self.logger.debug("The call names no Operator.")
            return None
        try:
            return UUID(str(raw))
        except ValueError as error:
            self.logger.error("The Operator identifier of %s is not a UUID.", request.url.path)
            raise SEAccessWrongOperatorError("The Operator identifier is malformed.") from error

    ############################
    # Publicly Exposed Methods #
    ############################

    async def __call__(self, request: Request) -> Caller:
        """Check a call.

        Args:
            request (Request): The request.

        Returns:
            Caller: The verified caller.

        Raises:
            SEAccessError: If the call is refused.
            SEKeycloakError: If the identity provider cannot be asked.
        """
        token = self._token(request)
        operator_id = self._operator_id(request)
        service: AccessService = getattr(request.app.state, AccessHandlers.ACCESS_SERVICE_STATE)
        caller = await service.authorise(token, self.roles, operator_id)
        self.logger.debug("The call to %s is authorised.", request.url.path)
        return caller
