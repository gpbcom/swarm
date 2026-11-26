from __future__ import annotations

# Standard library imports
from typing import ClassVar


class NatsHeaders:
    """The names of the NATS message headers Swarm reads and writes, and the pattern of an idempotency key.

    Attributes:
        IDEMPOTENCY_KEY (str): Header carrying the idempotency key of a request.
        DEADLINE (str): Header carrying the absolute UTC deadline, in ISO 8601 with microseconds.
        ERROR (str): Header carrying the class name of the error that failed a request.
        MSG_ID (str): The JetStream deduplication header.
        IDEMPOTENCY_KEY_PATTERN (str): Regular expression an idempotency key must match.

    Notes:
        The idempotency key is also a JetStream key-value key, so dots and spaces are refused.
    """

    IDEMPOTENCY_KEY: ClassVar[str] = "Swarm-Idempotency-Key"
    DEADLINE: ClassVar[str] = "Swarm-Deadline"
    ERROR: ClassVar[str] = "Swarm-Error"
    MSG_ID: ClassVar[str] = "Nats-Msg-Id"
    IDEMPOTENCY_KEY_PATTERN: ClassVar[str] = r"^[A-Za-z0-9_=-]+$"
