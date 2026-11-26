from __future__ import annotations

# First-party imports
from swarm_models.config.nats.exceptions.durable_consumer_config.se_invalid_durable_consumer_config_exception import (
    SEInvalidDurableConsumerConfigException,
)


class SEDurableConsumerConfigInvalidBatchSize(SEInvalidDurableConsumerConfigException):
    """Exception raised when an invalid ``batch_size`` is provided."""
