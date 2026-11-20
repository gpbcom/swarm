from __future__ import annotations

# First-party imports
from swarm_logging.models.exceptions.configurator.se_logging_error import SELoggingError


class SELoggingConfigurationUnreadableError(SELoggingError):
    """Raised when the logging configuration file cannot be read."""
