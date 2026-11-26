from __future__ import annotations

# First-party imports
from swarm_models.auth.exceptions.config.se_invalid_auth_config_exception import SEInvalidAuthConfigException


class SEAuthConfigInvalidAudience(SEInvalidAuthConfigException):
    """Exception raised when an invalid ``audience`` is provided."""
