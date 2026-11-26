from __future__ import annotations

# First-party imports
from swarm_models.live.feed.exceptions.se_live_error import SELiveError


class SELiveFeedNotReadyError(SELiveError):
    """Raised when a live source is asked of a live feed that is not initialised or is already closed."""
