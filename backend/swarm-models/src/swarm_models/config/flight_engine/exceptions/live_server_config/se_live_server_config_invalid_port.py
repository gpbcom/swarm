from __future__ import annotations

# First-party imports
from swarm_models.config.flight_engine.exceptions.live_server_config.se_invalid_live_server_config_exception import (
    SEInvalidLiveServerConfigException,
)


class SELiveServerConfigInvalidPort(SEInvalidLiveServerConfigException):
    """Exception raised when an invalid ``port`` is provided."""
