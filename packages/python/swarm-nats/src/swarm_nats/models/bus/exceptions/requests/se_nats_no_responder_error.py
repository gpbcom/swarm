from __future__ import annotations

# First-party imports
from swarm_nats.models.bus.exceptions.se_nats_error import SENatsError


class SENatsNoResponderError(SENatsError):
    """Raised when no responder is listening on the subject of a request."""
