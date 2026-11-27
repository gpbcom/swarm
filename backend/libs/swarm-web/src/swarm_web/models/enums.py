from __future__ import annotations

# Standard library imports
from enum import StrEnum, unique


@unique
class SignalAttribute(StrEnum):
    """The attributes a signal may carry.

    Attributes:
        OPERATOR_ID: The Operator the signal belongs to, a resource attribute.
        MISSION_ID: The Mission the signal belongs to, a resource attribute.
        CELL: The cell that emits the signal, a resource attribute.
        DRONE_ID: The Drone a signal is about, never a metric label.
    """

    OPERATOR_ID = "operator_id"
    MISSION_ID = "mission_id"
    CELL = "cell"
    DRONE_ID = "drone_id"
