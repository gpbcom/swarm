from __future__ import annotations

# Standard library imports
from logging import Logger, getLogger
from typing import ClassVar, Optional

# Third-party imports
from fastapi import FastAPI

# First-party imports
from gateway.api.rest.auth.access_error_handler import AccessErrorHandler
from gateway.models.access.exceptions import SEAccessError
from gateway.models.auth.auth_config import AuthConfig
from gateway.models.keycloak.exceptions import SEKeycloakError
from gateway.service.auth.access_service import AccessService


class AccessInstaller:
    """Puts the access check on an application: its service and the answer to its refusals.

    Attributes:
        ACCESS_SERVICE_STATE (ClassVar[str]): The name of the app state entry that holds the access service.
        logger (Logger): Logger instance.
    """

    ACCESS_SERVICE_STATE: ClassVar[str] = "access_service"

    def __init__(self, logger: Optional[Logger] = None) -> None:
        """Initialise the installer.

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
        handler = AccessErrorHandler()
        for error_type in (SEAccessError, SEKeycloakError):
            app.add_exception_handler(error_type, handler)
        self.logger.debug("The access check is installed.")
