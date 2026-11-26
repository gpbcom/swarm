from __future__ import annotations

# Standard library imports
from enum import StrEnum, unique


@unique
class MessageProblem(StrEnum):
    """What is wrong with a message of a catalogue.

    Attributes:
        MISSING (str): The message has no entry in the catalogue of the language.
        EMPTY (str): The entry exists but its translation is empty.
        FUZZY (str): The entry is marked fuzzy, so its translation is not reviewed.
    """

    MISSING = "missing"
    EMPTY = "empty"
    FUZZY = "fuzzy"
