from __future__ import annotations

# Standard library imports
from enum import StrEnum, unique


@unique
class DroneState(StrEnum):
    """The state of a Drone, with the names of the glossary.

    Attributes:
        READY (str): The Drone is airworthy, charged and available for a Squad.
        GROUNDED (str): The Drone may not fly.
        AIRBORNE (str): The Drone is flying its part of a Mission.
        RETURNING (str): The Drone is flying back to its take-off point or its Dock.
        LANDED (str): The Drone is on the ground after a flight.
        LOST (str): Ground control has no Link to the Drone, through any path.
    """

    READY = "ready"
    GROUNDED = "grounded"
    AIRBORNE = "airborne"
    RETURNING = "returning"
    LANDED = "landed"
    LOST = "lost"
