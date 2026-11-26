from __future__ import annotations

# Standard library imports
from typing import ClassVar

# First-party imports
from gateway.models.access.exceptions.se_access_error import SEAccessError
from gateway.models.enums import AccessRefusal


class SEAccessInvalidTokenError(SEAccessError):
    """Raised when a bearer token is malformed, wrongly signed or not meant for this gateway.

    Attributes:
        REFUSAL (AccessRefusal): The refusal this error stands for.
    """

    REFUSAL: ClassVar[AccessRefusal] = AccessRefusal.INVALID_TOKEN
