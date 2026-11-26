from __future__ import annotations

# First-party imports
from swarm_models.live.exceptions.se_invalid_live_subscription_exception import (
    SEInvalidLiveSubscriptionException,
)


class SELiveSubscriptionInvalidOp(SEInvalidLiveSubscriptionException):
    """Exception raised when an invalid ``op`` is provided."""
