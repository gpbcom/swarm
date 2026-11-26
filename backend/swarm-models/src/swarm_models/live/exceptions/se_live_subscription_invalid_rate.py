from __future__ import annotations

# First-party imports
from swarm_models.live.exceptions.se_invalid_live_subscription_exception import (
    SEInvalidLiveSubscriptionException,
)


class SELiveSubscriptionInvalidRate(SEInvalidLiveSubscriptionException):
    """Exception raised when an invalid ``rate`` is provided."""
