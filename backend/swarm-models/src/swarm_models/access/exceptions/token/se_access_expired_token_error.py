from __future__ import annotations

# Standard library imports
from typing import ClassVar

# First-party imports
from gateway.models.access.exceptions.se_access_error import SEAccessError
from gateway.models.enums import AccessRefusal


class SEAccessExpiredTokenError(SEAccessError):
    """Raised when a bearer token is past its expiry.

    Attributes:
        REFUSAL (AccessRefusal): The refusal this error stands for.
    """

    REFUSAL: ClassVar[AccessRefusal] = AccessRefusal.EXPIRED_TOKEN
