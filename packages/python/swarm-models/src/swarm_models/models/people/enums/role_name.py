from __future__ import annotations

# Standard library imports
from enum import StrEnum, unique


@unique
class RoleName(StrEnum):
    """The seven roles a person can hold.

    Attributes:
        PILOT (str): Flies Missions.
        MISSION_PLANNER (str): Designs Missions.
        FLEET_MAINTAINER (str): Maintains the Drones of an Operator.
        INSTRUCTOR (str): Instructs the people of an Operator.
        CLIENT (str): Orders and receives Deliverables.
        SITE_AGENT (str): Acts on a site for an Operator.
        SWARM_ADMINISTRATOR (str): Administers Swarm, with no access to the data of Operators.

    Notes:
        **Every role except ``SWARM_ADMINISTRATOR`` belongs to one Operator**, and a Swarm administrator belongs to
        none.
    """

    PILOT = "pilot"
    MISSION_PLANNER = "mission_planner"
    FLEET_MAINTAINER = "fleet_maintainer"
    INSTRUCTOR = "instructor"
    CLIENT = "client"
    SITE_AGENT = "site_agent"
    SWARM_ADMINISTRATOR = "swarm_administrator"
