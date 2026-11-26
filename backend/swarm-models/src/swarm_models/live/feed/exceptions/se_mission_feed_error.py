from __future__ import annotations

# First-party imports
from swarm_models.live.feed.exceptions.se_live_error import SELiveError


class SEMissionFeedError(SELiveError):
    """Raised when NATS refuses a subscription or an unsubscription of the mission feed."""
