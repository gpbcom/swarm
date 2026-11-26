from __future__ import annotations

# Standard library imports
from enum import StrEnum, unique


@unique
class ActorKind(StrEnum):
    """The kind of the author of an event.

    Attributes:
        PERSON (str): A person acting directly.
        SWARM_AGENT (str): A Swarm agent, which may act for a person.
        OUTSIDE_AGENT (str): An outside agent, which always acts for a person.
    """

    PERSON = "person"
    SWARM_AGENT = "swarm_agent"
    OUTSIDE_AGENT = "outside_agent"
