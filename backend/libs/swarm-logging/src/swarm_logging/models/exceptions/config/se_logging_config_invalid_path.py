from __future__ import annotations

# First-party imports
from swarm_logging.models.exceptions.config.se_invalid_logging_config_exception import (
    SEInvalidLoggingConfigException,
)


class SELoggingConfigInvalidPath(SEInvalidLoggingConfigException):
    """Exception raised when an invalid ``path`` is provided."""
