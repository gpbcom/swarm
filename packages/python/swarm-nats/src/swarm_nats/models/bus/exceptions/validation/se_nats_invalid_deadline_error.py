from __future__ import annotations

# First-party imports
from swarm_nats.models.bus.exceptions.se_nats_error import SENatsError


class SENatsInvalidDeadlineError(SENatsError):
    """Raised when a deadline is missing, malformed or already past."""
