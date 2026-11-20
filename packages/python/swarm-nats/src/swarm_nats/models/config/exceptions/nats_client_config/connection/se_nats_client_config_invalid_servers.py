from __future__ import annotations

# First-party imports
from swarm_nats.models.config.exceptions.nats_client_config.se_invalid_nats_client_config_exception import (
    SEInvalidNatsClientConfigException,
)


class SENatsClientConfigInvalidServers(SEInvalidNatsClientConfigException):
    """Exception raised when an invalid ``servers`` is provided."""
