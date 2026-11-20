from __future__ import annotations

# First-party imports
from swarm_nats.models.bus.exceptions.se_nats_error import SENatsError


class SENatsRequestDeadlineExceededError(SENatsError):
    """Raised when a request gets no reply before its deadline."""
