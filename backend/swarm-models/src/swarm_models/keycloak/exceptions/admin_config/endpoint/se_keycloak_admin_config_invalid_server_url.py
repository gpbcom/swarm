from __future__ import annotations

# First-party imports
from swarm_models.keycloak.exceptions.admin_config.se_invalid_keycloak_admin_config_exception import (
    SEInvalidKeycloakAdminConfigException,
)


class SEKeycloakAdminConfigInvalidServerUrl(SEInvalidKeycloakAdminConfigException):
    """Exception raised when an invalid ``server_url`` is provided."""
