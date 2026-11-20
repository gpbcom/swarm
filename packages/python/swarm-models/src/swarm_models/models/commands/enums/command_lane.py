"""The lanes of command."""

from __future__ import annotations

# Standard library imports
from enum import StrEnum, unique


@unique
class CommandLane(StrEnum):
    """The lane a command travels in.

    Attributes:
        SAFETY (str): The lane that always jumps the queue.
        NORMAL (str): The lane of every other command.
    """

    SAFETY = "safety"
    NORMAL = "normal"
