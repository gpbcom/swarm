from __future__ import annotations

# Standard library imports
from typing import ClassVar

# First-party imports
from gateway.models.access.exceptions.se_access_error import SEAccessError
from gateway.models.enums import AccessRefusal


class SEAccessWrongOperatorError(SEAccessError):
    """Raised when the caller's Operator is not the Operator the call targets.

    Attributes:
        REFUSAL (AccessRefusal): The refusal this error stands for.
    """

    REFUSAL: ClassVar[AccessRefusal] = AccessRefusal.WRONG_OPERATOR
