from __future__ import annotations

# Standard library imports
from http import HTTPStatus
from logging import Logger, getLogger
from typing import ClassVar, Dict, Optional

# Third-party imports
from fastapi import Request
from fastapi.responses import Response

# First-party imports
from gateway.models.access.exceptions import SEAccessError
from gateway.models.enums import AccessRefusal
from gateway.models.keycloak.exceptions import SEKeycloakError
from swarm_api.handlers.problem_handlers import ProblemHandlers


class AccessErrorHandler:
    """Answers a refused call as an ``application/problem+json`` document.

    Attributes:
        STATUS_OF_REFUSAL (ClassVar[Dict[AccessRefusal, HTTPStatus]]): The status of each refusal.
        WWW_AUTHENTICATE (ClassVar[str]): The name of the header that tells how to authenticate.
        BEARER (ClassVar[str]): The authentication scheme to use.
        logger (Logger): Logger instance.

    Notes:
        - **The token and the header that carried it are never logged or answered.**
        - A wrong Operator is answered ``404``, so that nobody learns another Operator's resources exist (BR-008).
        - The handler takes an ``Exception``, because Starlette types an exception handler that way. It narrows it to
          ``SEAccessError`` or ``SEKeycloakError`` and raises any other error again.
    """

    STATUS_OF_REFUSAL: ClassVar[Dict[AccessRefusal, HTTPStatus]] = {
        AccessRefusal.MISSING_TOKEN: HTTPStatus.UNAUTHORIZED,
        AccessRefusal.INVALID_TOKEN: HTTPStatus.UNAUTHORIZED,
        AccessRefusal.EXPIRED_TOKEN: HTTPStatus.UNAUTHORIZED,
        AccessRefusal.MISSING_ROLE: HTTPStatus.FORBIDDEN,
        AccessRefusal.WRONG_OPERATOR: HTTPStatus.NOT_FOUND,
        AccessRefusal.IDENTITY_UNAVAILABLE: HTTPStatus.SERVICE_UNAVAILABLE,
    }
    WWW_AUTHENTICATE: ClassVar[str] = "WWW-Authenticate"
    BEARER: ClassVar[str] = "Bearer"

    def __init__(self, logger: Optional[Logger] = None) -> None:
        """Initialise the handler.

        Args:
            logger (Optional[Logger]): Logger instance.
        """
        self.logger = logger if logger else getLogger(__name__)

    ############################
    # Publicly Exposed Methods #
    ############################

    async def __call__(self, request: Request, error: Exception) -> Response:
        """Answer one refusal.

        Args:
            request (Request): The request that was refused.
            error (Exception): The refusal, a ``SEAccessError`` or a ``SEKeycloakError``.

        Returns:
            Response: The problem document, with ``WWW-Authenticate`` for a status ``401``.

        Raises:
            Exception: The error itself, when it is not a refusal.
        """
        if not isinstance(error, (SEAccessError, SEKeycloakError)):
            self.logger.error("The access handler got an error that is no refusal: %s.", type(error).__name__)
            raise error
        refusal = error.REFUSAL
        status = self.STATUS_OF_REFUSAL[refusal]
        self.logger.warning("Refused %s %s: %s.", request.method, request.url.path, refusal.value)
        response = ProblemHandlers.problem_response(status, status.phrase, refusal.value, request.url.path)
        if status == HTTPStatus.UNAUTHORIZED:
            self.logger.debug("Adding the authentication challenge.")
            response.headers[self.WWW_AUTHENTICATE] = self.BEARER
        else:
            self.logger.debug("No authentication challenge for status %d.", status)
        return response
