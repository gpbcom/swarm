from __future__ import annotations

# First-party imports
from swarm_models.live.feed.exceptions.config.se_invalid_live_config_exception import SEInvalidLiveConfigException


class SELiveConfigInvalidStatusInterval(SEInvalidLiveConfigException):
    """Exception raised when an invalid ``status_interval_s`` is provided."""
