from __future__ import annotations

# First-party imports
from swarm_models.config.gateway.exceptions.gateway_config.se_invalid_gateway_config_exception import (
    SEInvalidGatewayConfigException,
)


class SEGatewayConfigInvalidOperators(SEInvalidGatewayConfigException):
    """Exception raised when an invalid ``operators`` is provided."""
