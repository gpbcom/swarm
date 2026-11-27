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
        SIMULATOR: The simulator, ``backend/apps/simulator``.
        FLIGHT_ENGINE: The flight engine of an edge, ``backend/apps/flight-engine``: a value has no hyphen, so the
            folder writes its underscore as a hyphen.
    """

    GATEWAY = "gateway"
    FLEET = "fleet"
    MISSIONS = "missions"
    SIMULATOR = "simulator"
    FLIGHT_ENGINE = "flight_engine"


@unique
class SimulatedDroneKind(StrEnum):
    """The kinds of simulated drone.

    Attributes:
        SYNTHETIC: A drone that a built-in program flies.
        PX4_SITL: A PX4 software-in-the-loop drone.
    """

    SYNTHETIC = "synthetic"
    PX4_SITL = "px4_sitl"


@unique
class FlightLogEntryKind(StrEnum):
    """The kinds of entry of a flight log.

    Attributes:
        ROUTE_UPLOADED: A route was uploaded to the drone.
        ARMED: The drone was armed.
        ROUTE_STARTED: The drone started its route.
        WAYPOINT_REACHED: The drone reached a waypoint.
        ROUTE_COMPLETED: The drone completed its route.
        ROUTE_FAILED: The route failed.
        COMMAND_ACCEPTED: A command was accepted.
        COMMAND_REFUSED: A command was refused.
    """

    ROUTE_UPLOADED = "route_uploaded"
    ARMED = "armed"
    ROUTE_STARTED = "route_started"
    WAYPOINT_REACHED = "waypoint_reached"
    ROUTE_COMPLETED = "route_completed"
    ROUTE_FAILED = "route_failed"
    COMMAND_ACCEPTED = "command_accepted"
    COMMAND_REFUSED = "command_refused"


@unique
class CommandVerdict(StrEnum):
    """The verdict on a command.

    Attributes:
        ACCEPTED: The drone accepted the command.
        REFUSED: The command was refused.
    """

    ACCEPTED = "accepted"
    REFUSED = "refused"


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


@unique
class Deployment(StrEnum):
    """Where an Operator's Swarm runs.

    Attributes:
        CLOUD: The Swarm runs in a cloud cell.
        ON_PREMISES: The Swarm runs on the Operator's own premises.
    """

    CLOUD = "cloud"
    ON_PREMISES = "on_premises"


@unique
class Jurisdiction(StrEnum):
    """A regulatory jurisdiction an Operator flies under.

    Attributes:
        EU_EASA: The European Union, under EASA rules.
        US_FAA: The United States, under FAA rules.
    """

    EU_EASA = "eu_easa"
    US_FAA = "us_faa"


@unique
class LlmProvider(StrEnum):
    """The kind of language model the AI agents of an Operator use.

    Attributes:
        CLAUDE: The Claude models.
        OPEN_WEIGHT: An open-weight model run by the Operator.
    """

    CLAUDE = "claude"
    OPEN_WEIGHT = "open_weight"


@unique
class Anchoring(StrEnum):
    """How the Evidence records of an Operator are anchored in time.

    Attributes:
        QUALIFIED_TIMESTAMPING: A qualified timestamping authority seals the records.
        PUBLIC_BLOCKCHAIN: A public blockchain seals the records.
        NONE: The records are not anchored.
    """

    QUALIFIED_TIMESTAMPING = "qualified_timestamping"
    PUBLIC_BLOCKCHAIN = "public_blockchain"
    NONE = "none"


@unique
class OperatorField(StrEnum):
    """A field of the request that creates an Operator, named in a refusal.

    Attributes:
        NAME: The name of the Operator.
        DEPLOYMENT: Where the Operator's Swarm runs.
        JURISDICTIONS: The jurisdictions the Operator flies under.
        FIRST_MISSION_PLANNER_EMAIL: The email address of the first Mission planner.
    """

    NAME = "name"
    DEPLOYMENT = "deployment"
    JURISDICTIONS = "jurisdictions"
    FIRST_MISSION_PLANNER_EMAIL = "first_mission_planner_email"
