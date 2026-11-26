from __future__ import annotations

# First-party imports
from swarm_nats.models.bus.exceptions.se_nats_error import SENatsError


class SENatsInvalidIdempotencyKeyError(SENatsError):
    """Raised when an idempotency key does not match its pattern."""
