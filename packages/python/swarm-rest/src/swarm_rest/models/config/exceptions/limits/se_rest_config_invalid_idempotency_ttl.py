from __future__ import annotations

# First-party imports
from swarm_rest.models.config.exceptions.se_invalid_rest_config_exception import (
    SEInvalidRestConfigException,
)


class SERestConfigInvalidIdempotencyTtl(SEInvalidRestConfigException):
    """Exception raised when an invalid ``idempotency_ttl_s`` is provided."""
