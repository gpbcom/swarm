from __future__ import annotations

# First-party imports
from swarm_models.live.exceptions.messages.se_live_error import SELiveError


class SELiveMessageUnreadable(SELiveError):
    """Raised when a live message is not valid MessagePack or not the model that was expected."""
