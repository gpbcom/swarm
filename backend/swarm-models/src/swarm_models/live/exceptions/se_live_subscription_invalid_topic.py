from __future__ import annotations

# First-party imports
from swarm_models.live.exceptions.se_invalid_live_subscription_exception import (
    SEInvalidLiveSubscriptionException,
)


class SELiveSubscriptionInvalidTopic(SEInvalidLiveSubscriptionException):
    """Exception raised when an invalid ``topic`` is provided."""
