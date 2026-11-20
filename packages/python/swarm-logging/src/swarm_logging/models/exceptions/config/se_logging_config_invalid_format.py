from __future__ import annotations

# First-party imports
from swarm_logging.models.exceptions.config.se_invalid_logging_config_exception import (
    SEInvalidLoggingConfigException,
)


class SELoggingConfigInvalidFormat(SEInvalidLoggingConfigException):
    """Exception raised when an invalid ``format`` is provided."""
