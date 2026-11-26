from __future__ import annotations

# First-party imports
from swarm_models.models.telemetry.exceptions.squad_frame.se_invalid_squad_frame_exception import (
    SEInvalidSquadFrameException,
)


class SESquadFrameInvalidTUs(SEInvalidSquadFrameException):
    """Exception raised when an invalid ``t_us`` is provided."""
