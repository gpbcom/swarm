from __future__ import annotations

# Standard library imports
from typing import ClassVar

# First-party imports
from swarm_models.access.exceptions.se_access_error import SEAccessError
from swarm_models.enums import AccessRefusal


class SEAccessExpiredTokenError(SEAccessError):
    """Raised when a bearer token is past its expiry.

    Attributes:
        REFUSAL (AccessRefusal): The refusal this error stands for.
    """

    REFUSAL: ClassVar[AccessRefusal] = AccessRefusal.EXPIRED_TOKEN
