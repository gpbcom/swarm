from __future__ import annotations

# Standard library imports
from enum import StrEnum, unique


@unique
class Language(StrEnum):
    """A language in which Swarm shows its screens.

    Attributes:
        ENGLISH: English, the default language.
        FRENCH: French.
        GERMAN: German.
        SPANISH: Spanish.
    """

    ENGLISH = "en"
    FRENCH = "fr"
    GERMAN = "de"
    SPANISH = "es"


@unique
class LiveOperation(StrEnum):
    """An operation a client asks of the live WebSocket.

    Attributes:
        SUBSCRIBE: Subscribe to a topic.
    """

    SUBSCRIBE = "subscribe"


@unique
class LiveTopicKind(StrEnum):
    """The kind of a live topic, the last part of its name.

    Attributes:
        SQUAD: The frames of the whole Squad of a Mission.
    """

    SQUAD = "squad"


@unique
class LiveRate(StrEnum):
    """How often a subscriber receives frames.

    Attributes:
        FULL: Every frame, at the rate of the source.
    """

    FULL = "full"
