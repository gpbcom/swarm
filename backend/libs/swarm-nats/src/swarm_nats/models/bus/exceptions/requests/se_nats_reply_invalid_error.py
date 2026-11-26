from __future__ import annotations

# First-party imports
from swarm_nats.models.bus.exceptions.se_nats_error import SENatsError


class SENatsReplyInvalidError(SENatsError):
    """Raised when the reply to a request cannot be read."""
