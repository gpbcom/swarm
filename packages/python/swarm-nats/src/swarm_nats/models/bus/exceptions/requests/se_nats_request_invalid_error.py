from __future__ import annotations

# First-party imports
from swarm_nats.models.bus.exceptions.se_nats_error import SENatsError


class SENatsRequestInvalidError(SENatsError):
    """Raised when a request cannot be built or sent."""
