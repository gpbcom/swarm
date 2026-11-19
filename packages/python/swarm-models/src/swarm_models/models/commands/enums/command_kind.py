"""The kinds of command."""

from __future__ import annotations

# Standard library imports
from enum import StrEnum, unique


@unique
class CommandKind(StrEnum):
    """What a command asks a Drone or a Squad to do.

    Attributes:
        HOLD (str): Hold the position.
        ABORT (str): Abort the Mission.
        RETURN_HOME (str): Return home.
        MANUAL_CONTROL (str): Hand the control to the Operator.
    """

    HOLD = "hold"
    ABORT = "abort"
    RETURN_HOME = "return_home"
    MANUAL_CONTROL = "manual_control"
