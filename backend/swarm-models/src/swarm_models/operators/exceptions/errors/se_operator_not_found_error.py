from __future__ import annotations

# Standard library imports
from http import HTTPStatus
from typing import ClassVar

# First-party imports
from swarm_web.models.rest.exceptions import SERestError


class SEOperatorNotFoundError(SERestError):
    """Raised when an Operator cannot be found.

    Attributes:
        STATUS (int): The HTTP status the error is answered with.
        TITLE (str): The short title of the problem, the standard phrase of ``STATUS``.
    """

    STATUS: ClassVar[int] = 404
    TITLE: ClassVar[str] = HTTPStatus(STATUS).phrase
