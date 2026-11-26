from __future__ import annotations

# First-party imports
from swarm_models.config.nats.exceptions.nats_responder_config.se_invalid_nats_responder_config_exception import (
    SEInvalidNatsResponderConfigException,
)


class SENatsResponderConfigInvalidIdempotencyBucket(SEInvalidNatsResponderConfigException):
    """Exception raised when an invalid ``idempotency_bucket`` is provided."""
