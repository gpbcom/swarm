from __future__ import annotations

# Standard library imports
from http import HTTPStatus
from typing import ClassVar

# First-party imports
from swarm_rest.models.rest.exceptions.se_rest_error import SERestError


class SEIdempotencyKeyMissingError(SERestError):
    """Raised when a POST carries no ``Idempotency-Key`` header.

    Attributes:
        STATUS (int): The HTTP status the error is answered with.
        TITLE (str): The short title of the problem, the standard phrase of ``STATUS``.
    """

    STATUS: ClassVar[int] = 400
    TITLE: ClassVar[str] = HTTPStatus(STATUS).phrase
