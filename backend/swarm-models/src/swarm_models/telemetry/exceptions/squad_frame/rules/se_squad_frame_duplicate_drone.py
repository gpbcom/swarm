from __future__ import annotations

# First-party imports
from swarm_models.models.telemetry.exceptions.squad_frame.se_invalid_squad_frame_exception import (
    SEInvalidSquadFrameException,
)


class SESquadFrameDuplicateDrone(SEInvalidSquadFrameException):
    """Exception raised when two frames of one SquadFrame come from the same Drone."""
