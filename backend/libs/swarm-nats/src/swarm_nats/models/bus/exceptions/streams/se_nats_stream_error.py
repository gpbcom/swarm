from __future__ import annotations

# First-party imports
from swarm_nats.models.bus.exceptions.se_nats_error import SENatsError


class SENatsStreamError(SENatsError):
    """Raised when a JetStream stream cannot be created or changed."""
