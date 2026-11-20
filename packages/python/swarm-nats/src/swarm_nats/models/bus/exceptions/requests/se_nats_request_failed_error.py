from __future__ import annotations

# First-party imports
from swarm_nats.models.bus.exceptions.se_nats_error import SENatsError


class SENatsRequestFailedError(SENatsError):
    """Raised when a responder answers a request with an error."""
