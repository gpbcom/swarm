from __future__ import annotations

# First-party imports
from gateway.models.live.exceptions.config.se_invalid_live_config_exception import SEInvalidLiveConfigException


class SELiveConfigInvalidSession(SEInvalidLiveConfigException):
    """Exception raised when an invalid ``session`` is provided."""
