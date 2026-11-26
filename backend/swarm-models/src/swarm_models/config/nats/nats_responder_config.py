from __future__ import annotations

# Standard library imports
import re
from typing import ClassVar, Literal, Pattern

# Third-party imports
from pydantic import BaseModel, ConfigDict, Field, JsonValue, field_validator

# First-party imports
from swarm_nats.models.config.exceptions import (
    SENatsResponderConfigInvalidIdempotencyBucket,
    SENatsResponderConfigInvalidIdempotencyTtl,
    SENatsResponderConfigInvalidQueueGroup,
    SENatsResponderConfigInvalidReplicas,
    SENatsResponderConfigInvalidStatusInterval,
    SENatsResponderConfigInvalidSubject,
)


class NatsResponderConfig(BaseModel):
    """The settings of a responder that answers requests on a subject.

    Attributes:
        subject (str): The subject to answer, wildcards allowed.
        queue_group (str): The queue group that shares the requests between responders.
        idempotency_bucket (str): The key-value bucket that remembers idempotency keys.
        idempotency_ttl_s (float): How long an idempotency key is remembered, in seconds.
        replicas (int): How many servers keep a copy of the idempotency bucket.
        status_interval_s (float): How often the responder yields its status, in seconds.
        SUBJECT_FIELD (str): The name of the ``subject`` field, for its validator.
        QUEUE_GROUP_FIELD (str): The name of the ``queue_group`` field, for its validator.
        IDEMPOTENCY_BUCKET_FIELD (str): The name of the ``idempotency_bucket`` field, for its validator.
        IDEMPOTENCY_TTL_FIELD (str): The name of the ``idempotency_ttl_s`` field, for its validator.
        REPLICAS_FIELD (str): The name of the ``replicas`` field, for its validator.
        STATUS_INTERVAL_FIELD (str): The name of the ``status_interval_s`` field, for its validator.
        DEFAULT_IDEMPOTENCY_BUCKET (str): The default bucket name.
        DEFAULT_IDEMPOTENCY_TTL_S (float): The default retention of a key, 24 hours.
        DEFAULT_REPLICAS (int): The default number of replicas, 3, as streams are replicated.
        DEFAULT_STATUS_INTERVAL_S (float): The default status interval.
        REPLICAS_MIN (int): The fewest replicas allowed.
        REPLICAS_MAX (int): The most replicas allowed, the maximum of JetStream.
        SUBJECT_PATTERN (Pattern[str]): Dot-separated tokens with no space and no empty token.
        QUEUE_GROUP_PATTERN (Pattern[str]): A name with no space.
        BUCKET_PATTERN (Pattern[str]): A name of letters, digits, underscores and hyphens.
        BEFORE (str): The validator mode that runs before Pydantic's own validation.

    Notes:
        - The idempotency TTL is the window in which a retried request gets the stored reply.
        - A boolean is refused where a number is expected.
    """

    SUBJECT_FIELD: ClassVar[str] = "subject"
    QUEUE_GROUP_FIELD: ClassVar[str] = "queue_group"
    IDEMPOTENCY_BUCKET_FIELD: ClassVar[str] = "idempotency_bucket"
    IDEMPOTENCY_TTL_FIELD: ClassVar[str] = "idempotency_ttl_s"
    REPLICAS_FIELD: ClassVar[str] = "replicas"
    STATUS_INTERVAL_FIELD: ClassVar[str] = "status_interval_s"
    DEFAULT_IDEMPOTENCY_BUCKET: ClassVar[str] = "idempotency"
    DEFAULT_IDEMPOTENCY_TTL_S: ClassVar[float] = 86400.0
    DEFAULT_REPLICAS: ClassVar[int] = 3
    DEFAULT_STATUS_INTERVAL_S: ClassVar[float] = 5.0
    REPLICAS_MIN: ClassVar[int] = 1
    REPLICAS_MAX: ClassVar[int] = 5
    SUBJECT_PATTERN: ClassVar[Pattern[str]] = re.compile(r"^[^\s.]+(\.[^\s.]+)*$")
    QUEUE_GROUP_PATTERN: ClassVar[Pattern[str]] = re.compile(r"^\S+$")
    BUCKET_PATTERN: ClassVar[Pattern[str]] = re.compile(r"^[A-Za-z0-9_-]+$")
    BEFORE: ClassVar[Literal["before"]] = "before"

    model_config = ConfigDict(extra="forbid", validate_default=True)

    subject: str = Field(description="The subject to answer, wildcards allowed. Required.")
    queue_group: str = Field(description="The queue group that shares the requests between responders. Required.")
    idempotency_bucket: str = Field(
        default=DEFAULT_IDEMPOTENCY_BUCKET,
        description="The key-value bucket that remembers idempotency keys. Defaults to idempotency.",
    )
    idempotency_ttl_s: float = Field(
        default=DEFAULT_IDEMPOTENCY_TTL_S,
        description="How long an idempotency key is remembered, in seconds. Defaults to 86400, 24 hours.",
    )
    replicas: int = Field(
        default=DEFAULT_REPLICAS,
        description="How many servers keep a copy of the bucket, from 1 to 5. Defaults to 3.",
    )
    status_interval_s: float = Field(
        default=DEFAULT_STATUS_INTERVAL_S,
        description="How often the responder yields its status, in seconds. Defaults to 5.",
    )

    @field_validator(SUBJECT_FIELD, mode=BEFORE)
    def validate_subject(cls, value: JsonValue) -> JsonValue:
        """Validate ``subject``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The stripped subject.

        Raises:
            SENatsResponderConfigInvalidSubject: If the value is not a well-formed subject.
        """
        if not isinstance(value, str) or not cls.SUBJECT_PATTERN.match(value.strip()):
            raise SENatsResponderConfigInvalidSubject(
                f"Invalid subject: {value!r}. Must be dot-separated tokens, with no space and no empty token."
            )
        return value.strip()

    @field_validator(QUEUE_GROUP_FIELD, mode=BEFORE)
    def validate_queue_group(cls, value: JsonValue) -> JsonValue:
        """Validate ``queue_group``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The stripped queue group.

        Raises:
            SENatsResponderConfigInvalidQueueGroup: If the value is not a non-empty name with no space.
        """
        if not isinstance(value, str) or not cls.QUEUE_GROUP_PATTERN.match(value.strip()):
            raise SENatsResponderConfigInvalidQueueGroup(
                f"Invalid queue_group: {value!r}. Must be a non-empty name with no space."
            )
        return value.strip()

    @field_validator(IDEMPOTENCY_BUCKET_FIELD, mode=BEFORE)
    def validate_idempotency_bucket(cls, value: JsonValue) -> JsonValue:
        """Validate ``idempotency_bucket``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The stripped bucket name, or the default when ``None``.

        Raises:
            SENatsResponderConfigInvalidIdempotencyBucket: If the value is not a bucket name.
        """
        if value is None:
            return cls.DEFAULT_IDEMPOTENCY_BUCKET
        if not isinstance(value, str) or not cls.BUCKET_PATTERN.match(value.strip()):
            raise SENatsResponderConfigInvalidIdempotencyBucket(
                f"Invalid idempotency_bucket: {value!r}. Must be letters, digits, underscores and hyphens only."
            )
        return value.strip()

    @field_validator(IDEMPOTENCY_TTL_FIELD, mode=BEFORE)
    def validate_idempotency_ttl_s(cls, value: JsonValue) -> JsonValue:
        """Validate ``idempotency_ttl_s``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The duration, or the default when ``None``.

        Raises:
            SENatsResponderConfigInvalidIdempotencyTtl: If the value is not a positive number.
        """
        if value is None:
            return cls.DEFAULT_IDEMPOTENCY_TTL_S
        if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
            raise SENatsResponderConfigInvalidIdempotencyTtl(
                f"Invalid idempotency_ttl_s: {value!r}. Must be a positive number."
            )
        return value

    @field_validator(REPLICAS_FIELD, mode=BEFORE)
    def validate_replicas(cls, value: JsonValue) -> JsonValue:
        """Validate ``replicas``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The number of replicas, or the default when ``None``.

        Raises:
            SENatsResponderConfigInvalidReplicas: If the value is not an integer within the bounds.
        """
        if value is None:
            return cls.DEFAULT_REPLICAS
        if isinstance(value, bool) or not isinstance(value, int) or not cls.REPLICAS_MIN <= value <= cls.REPLICAS_MAX:
            raise SENatsResponderConfigInvalidReplicas(
                f"Invalid replicas: {value!r}. Must be an integer in [{cls.REPLICAS_MIN}, {cls.REPLICAS_MAX}]."
            )
        return value

    @field_validator(STATUS_INTERVAL_FIELD, mode=BEFORE)
    def validate_status_interval_s(cls, value: JsonValue) -> JsonValue:
        """Validate ``status_interval_s``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The duration, or the default when ``None``.

        Raises:
            SENatsResponderConfigInvalidStatusInterval: If the value is not a positive number.
        """
        if value is None:
            return cls.DEFAULT_STATUS_INTERVAL_S
        if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
            raise SENatsResponderConfigInvalidStatusInterval(
                f"Invalid status_interval_s: {value!r}. Must be a positive number."
            )
        return value
