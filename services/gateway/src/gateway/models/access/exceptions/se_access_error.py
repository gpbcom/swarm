from __future__ import annotations

# Standard library imports
from typing import ClassVar

# First-party imports
from gateway.models.enums import AccessRefusal


class SEAccessError(Exception):
    """Base class for every refusal of a call by the gateway's access check.

    Attributes:
        REFUSAL (AccessRefusal): The refusal this error stands for, set by each subclass.
    """

    REFUSAL: ClassVar[AccessRefusal]
