from __future__ import annotations

# Standard library imports
from http import HTTPStatus
from typing import ClassVar

# First-party imports
from swarm_rest.models.rest.exceptions.se_rest_error import SERestError


class SEIdempotencyKeyInvalidError(SERestError):
    """Raised when an ``Idempotency-Key`` does not have the right shape.

    Attributes:
        STATUS (int): The HTTP status the error is answered with.
        TITLE (str): The short title of the problem, the standard phrase of ``STATUS``.
    """

    STATUS: ClassVar[int] = 400
    TITLE: ClassVar[str] = HTTPStatus(STATUS).phrase
