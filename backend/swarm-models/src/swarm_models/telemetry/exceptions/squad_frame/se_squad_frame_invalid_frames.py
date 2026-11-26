from __future__ import annotations

# First-party imports
from swarm_models.telemetry.exceptions.squad_frame.se_invalid_squad_frame_exception import (
    SEInvalidSquadFrameException,
)


class SESquadFrameInvalidFrames(SEInvalidSquadFrameException):
    """Exception raised when an invalid ``frames`` is provided."""
