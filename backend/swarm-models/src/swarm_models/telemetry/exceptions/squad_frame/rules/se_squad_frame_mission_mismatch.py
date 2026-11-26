from __future__ import annotations

# First-party imports
from swarm_models.models.telemetry.exceptions.squad_frame.se_invalid_squad_frame_exception import (
    SEInvalidSquadFrameException,
)


class SESquadFrameMissionMismatch(SEInvalidSquadFrameException):
    """Exception raised when a frame belongs to another Mission than its SquadFrame."""
