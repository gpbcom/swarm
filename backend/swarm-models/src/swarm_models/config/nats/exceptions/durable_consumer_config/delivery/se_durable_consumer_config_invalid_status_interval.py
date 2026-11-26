from __future__ import annotations

# First-party imports
from swarm_nats.models.config.exceptions.durable_consumer_config.se_invalid_durable_consumer_config_exception import (
    SEInvalidDurableConsumerConfigException,
)


class SEDurableConsumerConfigInvalidStatusInterval(SEInvalidDurableConsumerConfigException):
    """Exception raised when an invalid ``status_interval_s`` is provided."""
