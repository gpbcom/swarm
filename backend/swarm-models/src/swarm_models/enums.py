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


@unique
class AccessRefusal(StrEnum):
    """Why the gateway refused a call.

    Attributes:
        MISSING_TOKEN: The call carried no bearer token.
        INVALID_TOKEN: The token is malformed, wrongly signed or addressed to another issuer or audience.
        EXPIRED_TOKEN: The token is past its expiry.
        WRONG_OPERATOR: The token's Operator is not the Operator the call targets.
        MISSING_ROLE: The token lacks the role the call needs.
        IDENTITY_UNAVAILABLE: The identity provider could not be reached or its signing key is unknown.
    """

    MISSING_TOKEN = "missing_token"
    INVALID_TOKEN = "invalid_token"
    EXPIRED_TOKEN = "expired_token"
    WRONG_OPERATOR = "wrong_operator"
    MISSING_ROLE = "missing_role"
    IDENTITY_UNAVAILABLE = "identity_unavailable"


@unique
class TokenClaim(StrEnum):
    """The claims of an access token that the gateway reads.

    Attributes:
        SUBJECT: The subject, ``sub``.
        ISSUER: The issuer, ``iss``.
        AUDIENCE: The audience, ``aud``.
        EXPIRES_AT: The expiry time, ``exp``.
        ISSUED_AT: The issue time, ``iat``.
        OPERATOR_ID: The Operator the caller belongs to, ``operator_id``.
        REALM_ACCESS: The realm access section, ``realm_access``.
        ROLES: The list of roles inside the realm access section, ``roles``.
    """

    SUBJECT = "sub"
    ISSUER = "iss"
    AUDIENCE = "aud"
    EXPIRES_AT = "exp"
    ISSUED_AT = "iat"
    OPERATOR_ID = "operator_id"
    REALM_ACCESS = "realm_access"
    ROLES = "roles"


@unique
class AppName(StrEnum):
    """The apps of ``backend/apps/``, each built into its own image.

    Attributes:
        GATEWAY: The gateway, ``backend/apps/gateway``.
        FLEET: The fleet service, ``backend/apps/fleet``.
        MISSIONS: The missions service, ``backend/apps/missions``.
    """

    GATEWAY = "gateway"
    FLEET = "fleet"
    MISSIONS = "missions"
