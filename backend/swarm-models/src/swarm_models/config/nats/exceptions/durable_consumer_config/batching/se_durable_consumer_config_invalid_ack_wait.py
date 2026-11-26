from __future__ import annotations

# First-party imports
from swarm_models.config.nats.exceptions.durable_consumer_config.se_invalid_durable_consumer_config_exception import (
    SEInvalidDurableConsumerConfigException,
)


class SEDurableConsumerConfigInvalidAckWait(SEInvalidDurableConsumerConfigException):
    """Exception raised when an invalid ``ack_wait_s`` is provided."""
