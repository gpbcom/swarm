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


@unique
class CredentialKind(StrEnum):
    """The kind of identity a credential is issued to.

    Attributes:
        SERVICE (str): A Swarm service.
        EDGE (str): An edge node.
        SIMULATED (str): A simulated drone or node.
        SYSTEM (str): The system account.
    """

    SERVICE = "service"
    EDGE = "edge"
    SIMULATED = "simulated"
    SYSTEM = "system"


@unique
class NatsClaimType(StrEnum):
    """The type of a NATS JWT claim.

    Attributes:
        OPERATOR (str): The claim of an operator.
        ACCOUNT (str): The claim of an account.
        USER (str): The claim of a user.
    """

    OPERATOR = "operator"
    ACCOUNT = "account"
    USER = "user"


@unique
class StreamStorage(StrEnum):
    """Where a JetStream stream keeps its messages.

    Attributes:
        FILE (str): On disk.
        MEMORY (str): In memory.
    """

    FILE = "file"
    MEMORY = "memory"


@unique
class StreamRetention(StrEnum):
    """When a JetStream stream removes its messages.

    Attributes:
        LIMITS (str): When a size, age or count limit is reached.
        INTEREST (str): When no consumer is interested any more.
        WORK_QUEUE (str): When a consumer has acknowledged the message.
    """

    LIMITS = "limits"
    INTEREST = "interest"
    WORK_QUEUE = "work_queue"
