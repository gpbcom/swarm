from __future__ import annotations

# Standard library imports
from http import HTTPStatus
from typing import ClassVar


class SERestError(Exception):
    """Base class for every error the REST layer answers as a problem document.

    Attributes:
        STATUS (int): The HTTP status the error is answered with.
        TITLE (str): The short title of the problem, the standard phrase of ``STATUS``.
    """

    STATUS: ClassVar[int] = 500
    TITLE: ClassVar[str] = HTTPStatus(STATUS).phrase
