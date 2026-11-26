from __future__ import annotations

# Standard library imports
from typing import ClassVar

# First-party imports
from gateway.models.access.exceptions.se_access_error import SEAccessError
from gateway.models.enums import AccessRefusal


class SEAccessMissingTokenError(SEAccessError):
    """Raised when a call carries no bearer token.

    Attributes:
        REFUSAL (AccessRefusal): The refusal this error stands for.
    """

    REFUSAL: ClassVar[AccessRefusal] = AccessRefusal.MISSING_TOKEN
