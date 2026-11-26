from __future__ import annotations

# First-party imports
from swarm_nats.models.config.exceptions.durable_consumer_config.se_invalid_durable_consumer_config_exception import (
    SEInvalidDurableConsumerConfigException,
)


class SEDurableConsumerConfigInvalidFetchTimeout(SEInvalidDurableConsumerConfigException):
    """Exception raised when an invalid ``fetch_timeout_s`` is provided."""
