from __future__ import annotations

# Standard library imports
from enum import StrEnum, unique


@unique
class LogFormat(StrEnum):
    """How a log record is written.

    Attributes:
        COLOURED (str): Coloured, human readable lines, for the console.
        JSON (str): One JSON object per line, for production.
    """

    COLOURED = "coloured"
    JSON = "json"
