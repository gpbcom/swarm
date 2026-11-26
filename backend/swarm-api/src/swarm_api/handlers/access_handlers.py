from __future__ import annotations

# Standard library imports
from http import HTTPStatus
from logging import Logger, getLogger
from typing import ClassVar, Dict, Optional

# Third-party imports
from fastapi import FastAPI, Request
from fastapi.responses import Response

# First-party imports
from swarm_api.handlers.problem_handlers import ProblemHandlers
from swarm_models.access.exceptions import SEAccessError
from swarm_models.auth.auth_config import AuthConfig
from swarm_models.enums import AccessRefusal
from swarm_models.keycloak.exceptions import SEKeycloakError
from swarm_service.gateway.auth.access_service import AccessService


class AccessHandlers:
    """Installs the access check on an application, and answers each refusal as a problem document.

    Attributes:
        ACCESS_SERVICE_STATE (ClassVar[str]): The name of the app state entry that holds the access service.
        STATUS_OF_REFUSAL (ClassVar[Dict[AccessRefusal, HTTPStatus]]): The status of each refusal.
        WWW_AUTHENTICATE (ClassVar[str]): The name of the header that tells how to authenticate.
        BEARER (ClassVar[str]): The authentication scheme to use.
        logger (Logger): Logger instance.

    Notes:
        - **The token and the header that carried it are never logged or answered.**
        - A wrong Operator is answered ``404``, so that nobody learns another Operator's resources exist (BR-008).
        - The handler takes an ``Exception``, because Starlette types an exception handler that way. It narrows it to
          ``SEAccessError`` or ``SEKeycloakError`` and raises any other error again.
        - The installer and the handler of the refusals are one class, so that the access check has one class in the
          api layer.
    """

    ACCESS_SERVICE_STATE: ClassVar[str] = "access_service"

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
        """Initialise the handlers.

        Args:
            logger (Optional[Logger]): Logger instance.
        """
        self.logger = logger if logger else getLogger(__name__)

    ############################
    # Publicly Exposed Methods #
    ############################

    def install(self, app: FastAPI, config: AuthConfig) -> None:
        """Set the access service on the app state and register the handler of the refusals.

        Args:
            app (FastAPI): The application to install the access check on.
            config (AuthConfig): The configuration of the check of the tokens.
        """
        setattr(app.state, self.ACCESS_SERVICE_STATE, AccessService.from_config(config))
        for error_type in (SEAccessError, SEKeycloakError):
            app.add_exception_handler(error_type, self.handle)
        self.logger.debug("The access check is installed.")

    async def handle(self, request: Request, error: Exception) -> Response:
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
