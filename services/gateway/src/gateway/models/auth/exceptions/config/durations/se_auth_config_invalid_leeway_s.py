from __future__ import annotations

# First-party imports
from gateway.models.auth.exceptions.config.se_invalid_auth_config_exception import SEInvalidAuthConfigException


class SEAuthConfigInvalidLeewayS(SEInvalidAuthConfigException):
    """Exception raised when an invalid ``leeway_s`` is provided."""
