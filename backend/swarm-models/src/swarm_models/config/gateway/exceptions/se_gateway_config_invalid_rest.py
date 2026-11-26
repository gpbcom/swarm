from __future__ import annotations

# First-party imports
from gateway.models.config.exceptions.se_invalid_gateway_config_exception import SEInvalidGatewayConfigException


class SEGatewayConfigInvalidRest(SEInvalidGatewayConfigException):
    """Exception raised when an invalid ``rest`` is provided."""
