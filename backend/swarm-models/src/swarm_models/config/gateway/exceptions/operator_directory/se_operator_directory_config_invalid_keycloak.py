from __future__ import annotations

# First-party imports
from swarm_models.config.gateway.exceptions.operator_directory.se_invalid_operator_directory_config_exception import (
    SEInvalidOperatorDirectoryConfigException,
)


class SEOperatorDirectoryConfigInvalidKeycloak(SEInvalidOperatorDirectoryConfigException):
    """Exception raised when an invalid ``keycloak`` is provided."""
