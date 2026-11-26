from __future__ import annotations

# First-party imports
from swarm_models.live.feed.exceptions.config.se_invalid_live_config_exception import SEInvalidLiveConfigException


class SELiveConfigInvalidNats(SEInvalidLiveConfigException):
    """Exception raised when an invalid ``nats`` is provided."""
