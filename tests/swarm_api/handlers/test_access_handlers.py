from __future__ import annotations

# Standard library imports
from typing import ClassVar

# Third-party imports
from fastapi import FastAPI

# First-party imports
from swarm_api.handlers.access_handlers import AccessHandlers
from swarm_models.access.exceptions import SEAccessError
from swarm_models.auth.auth_config import AuthConfig
from swarm_models.keycloak.exceptions import SEKeycloakError
from swarm_service.gateway.auth.access_service import AccessService


class TestAccessInstaller:
    STATE_NAME: ClassVar[str] = "access_service"

    def test_the_state_name_is_access_service(self) -> None:
        assert AccessHandlers.ACCESS_SERVICE_STATE == self.STATE_NAME

    def test_the_access_service_is_set_on_the_app_state(self, auth_config: AuthConfig) -> None:
        app = FastAPI()

        AccessHandlers().install(app, auth_config)

        assert isinstance(getattr(app.state, AccessHandlers.ACCESS_SERVICE_STATE), AccessService)

    def test_a_handler_is_registered_for_access_and_keycloak_errors(self, auth_config: AuthConfig) -> None:
        app = FastAPI()

        AccessHandlers().install(app, auth_config)

        assert SEAccessError in app.exception_handlers
        assert SEKeycloakError in app.exception_handlers
