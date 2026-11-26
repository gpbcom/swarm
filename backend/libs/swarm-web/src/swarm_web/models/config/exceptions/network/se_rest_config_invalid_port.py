from __future__ import annotations

# First-party imports
from swarm_web.models.config.exceptions.se_invalid_rest_config_exception import (
    SEInvalidRestConfigException,
)


class SERestConfigInvalidPort(SEInvalidRestConfigException):
    """Exception raised when an invalid ``port`` is provided."""
