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
        TRACE_PARENT (str): W3C header carrying the trace and span of the sender.
        TRACE_STATE (str): W3C header carrying the vendor trace state.
        BAGGAGE (str): W3C header carrying the baggage.
        IDEMPOTENCY_KEY_PATTERN (str): Regular expression an idempotency key must match.

    Notes:
        The idempotency key is also a JetStream key-value key, so dots and spaces are refused.
    """

    IDEMPOTENCY_KEY: ClassVar[str] = "Swarm-Idempotency-Key"
    DEADLINE: ClassVar[str] = "Swarm-Deadline"
    ERROR: ClassVar[str] = "Swarm-Error"
    MSG_ID: ClassVar[str] = "Nats-Msg-Id"
    TRACE_PARENT: ClassVar[str] = "traceparent"
    TRACE_STATE: ClassVar[str] = "tracestate"
    BAGGAGE: ClassVar[str] = "baggage"
    IDEMPOTENCY_KEY_PATTERN: ClassVar[str] = r"^[A-Za-z0-9_=-]+$"
