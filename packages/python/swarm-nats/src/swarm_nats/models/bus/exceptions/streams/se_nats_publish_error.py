from __future__ import annotations

# First-party imports
from swarm_nats.models.bus.exceptions.se_nats_error import SENatsError


class SENatsPublishError(SENatsError):
    """Raised when an event cannot be published to JetStream."""
