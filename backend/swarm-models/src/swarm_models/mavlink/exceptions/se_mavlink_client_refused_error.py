from __future__ import annotations

# First-party imports
from swarm_models.mavlink.exceptions.se_mavlink_client_error import SEMavlinkClientError


class SEMavlinkClientRefusedError(SEMavlinkClientError):
    """Raised when a Drone refuses a mission or a command."""
