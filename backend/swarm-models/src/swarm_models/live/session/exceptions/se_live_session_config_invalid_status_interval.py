from __future__ import annotations

# First-party imports
from swarm_live.models.config.exceptions.se_invalid_live_session_config_exception import (
    SEInvalidLiveSessionConfigException,
)


class SELiveSessionConfigInvalidStatusInterval(SEInvalidLiveSessionConfigException):
    """Exception raised when an invalid ``status_interval_s`` is provided."""
