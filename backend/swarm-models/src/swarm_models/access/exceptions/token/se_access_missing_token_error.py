from __future__ import annotations

# Standard library imports
from typing import ClassVar

# First-party imports
from swarm_models.access.exceptions.se_access_error import SEAccessError
from swarm_models.enums import AccessRefusal


class SEAccessMissingTokenError(SEAccessError):
    """Raised when a call carries no bearer token.

    Attributes:
        REFUSAL (AccessRefusal): The refusal this error stands for.
    """

    REFUSAL: ClassVar[AccessRefusal] = AccessRefusal.MISSING_TOKEN
