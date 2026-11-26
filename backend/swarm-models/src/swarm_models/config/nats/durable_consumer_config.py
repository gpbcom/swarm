from __future__ import annotations

# Standard library imports
import re
from typing import ClassVar, Literal, Optional, Pattern

# Third-party imports
from pydantic import BaseModel, ConfigDict, Field, JsonValue, field_validator

# First-party imports
from swarm_models.config.nats.exceptions import (
    SEDurableConsumerConfigInvalidAckWait,
    SEDurableConsumerConfigInvalidBatchSize,
    SEDurableConsumerConfigInvalidDurableName,
    SEDurableConsumerConfigInvalidFetchTimeout,
    SEDurableConsumerConfigInvalidFilterSubject,
    SEDurableConsumerConfigInvalidMaxDeliver,
    SEDurableConsumerConfigInvalidStatusInterval,
    SEDurableConsumerConfigInvalidStream,
)


class DurableConsumerConfig(BaseModel):
    """The settings of a durable consumer that reads a JetStream stream.

    Attributes:
        stream (str): The stream to read.
        durable_name (str): The name that keeps the consumer's position between runs.
        filter_subject (Optional[str]): The subject to keep, or ``None`` for the whole stream.
        batch_size (int): How many messages one fetch asks for.
        fetch_timeout_s (float): How long one fetch waits for messages, in seconds.
        ack_wait_s (float): How long the server waits for an acknowledgement before it redelivers, in seconds.
        max_deliver (int): How many times a message is delivered, ``-1`` for unlimited.
        status_interval_s (float): How often the consumer yields its status, in seconds.
        STREAM_FIELD (str): The name of the ``stream`` field, for its validator.
        DURABLE_NAME_FIELD (str): The name of the ``durable_name`` field, for its validator.
        FILTER_SUBJECT_FIELD (str): The name of the ``filter_subject`` field, for its validator.
        BATCH_SIZE_FIELD (str): The name of the ``batch_size`` field, for its validator.
        FETCH_TIMEOUT_FIELD (str): The name of the ``fetch_timeout_s`` field, for its validator.
        ACK_WAIT_FIELD (str): The name of the ``ack_wait_s`` field, for its validator.
        MAX_DELIVER_FIELD (str): The name of the ``max_deliver`` field, for its validator.
        STATUS_INTERVAL_FIELD (str): The name of the ``status_interval_s`` field, for its validator.
        DEFAULT_BATCH_SIZE (int): The default batch size.
        DEFAULT_FETCH_TIMEOUT_S (float): The default fetch timeout.
        DEFAULT_ACK_WAIT_S (float): The default acknowledgement wait, 30 s as in NATS.
        DEFAULT_MAX_DELIVER (int): The default delivery limit, ``-1`` (unlimited) as in NATS.
        DEFAULT_STATUS_INTERVAL_S (float): The default status interval.
        BATCH_SIZE_MIN (int): The smallest batch size allowed.
        MAX_DELIVER_UNLIMITED (int): The value of ``max_deliver`` that means no limit.
        MAX_DELIVER_MIN (int): The smallest limited value of ``max_deliver``.
        NAME_PATTERN (Pattern[str]): A name of letters, digits, underscores and hyphens.
        SUBJECT_PATTERN (Pattern[str]): Dot-separated tokens with no space and no empty token.
        BEFORE (str): The validator mode that runs before Pydantic's own validation.

    Notes:
        - A boolean is refused where a number is expected.
        - The stream and durable names hold no dot, because NATS builds subjects from them.
    """

    STREAM_FIELD: ClassVar[str] = "stream"
    DURABLE_NAME_FIELD: ClassVar[str] = "durable_name"
    FILTER_SUBJECT_FIELD: ClassVar[str] = "filter_subject"
    BATCH_SIZE_FIELD: ClassVar[str] = "batch_size"
    FETCH_TIMEOUT_FIELD: ClassVar[str] = "fetch_timeout_s"
    ACK_WAIT_FIELD: ClassVar[str] = "ack_wait_s"
    MAX_DELIVER_FIELD: ClassVar[str] = "max_deliver"
    STATUS_INTERVAL_FIELD: ClassVar[str] = "status_interval_s"
    DEFAULT_BATCH_SIZE: ClassVar[int] = 100
    DEFAULT_FETCH_TIMEOUT_S: ClassVar[float] = 1.0
    DEFAULT_ACK_WAIT_S: ClassVar[float] = 30.0
    DEFAULT_MAX_DELIVER: ClassVar[int] = -1
    DEFAULT_STATUS_INTERVAL_S: ClassVar[float] = 5.0
    BATCH_SIZE_MIN: ClassVar[int] = 1
    MAX_DELIVER_UNLIMITED: ClassVar[int] = -1
    MAX_DELIVER_MIN: ClassVar[int] = 1
    NAME_PATTERN: ClassVar[Pattern[str]] = re.compile(r"^[A-Za-z0-9_-]+$")
    SUBJECT_PATTERN: ClassVar[Pattern[str]] = re.compile(r"^[^\s.]+(\.[^\s.]+)*$")
    BEFORE: ClassVar[Literal["before"]] = "before"

    model_config = ConfigDict(extra="forbid", validate_default=True)

    stream: str = Field(description="The stream to read. Required.")
    durable_name: str = Field(description="The name that keeps the consumer's position between runs. Required.")
    filter_subject: Optional[str] = Field(
        default=None,
        description="The subject to keep, wildcards allowed. Defaults to none, the whole stream.",
    )
    batch_size: int = Field(
        default=DEFAULT_BATCH_SIZE,
        description="How many messages one fetch asks for. Defaults to 100.",
    )
    fetch_timeout_s: float = Field(
        default=DEFAULT_FETCH_TIMEOUT_S,
        description="How long one fetch waits for messages, in seconds. Defaults to 1.",
    )
    ack_wait_s: float = Field(
        default=DEFAULT_ACK_WAIT_S,
        description="How long the server waits for an acknowledgement before it redelivers, in seconds. "
        "Defaults to 30, as in NATS.",
    )
    max_deliver: int = Field(
        default=DEFAULT_MAX_DELIVER,
        description="How many times a message is delivered, -1 for unlimited. Defaults to -1, as in NATS.",
    )
    status_interval_s: float = Field(
        default=DEFAULT_STATUS_INTERVAL_S,
        description="How often the consumer yields its status, in seconds. Defaults to 5.",
    )

    @field_validator(STREAM_FIELD, mode=BEFORE)
    def validate_stream(cls, value: JsonValue) -> JsonValue:
        """Validate ``stream``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The stripped stream name.

        Raises:
            SEDurableConsumerConfigInvalidStream: If the value is not a stream name.
        """
        if not isinstance(value, str) or not cls.NAME_PATTERN.match(value.strip()):
            raise SEDurableConsumerConfigInvalidStream(
                f"Invalid stream: {value!r}. Must be letters, digits, underscores and hyphens only."
            )
        return value.strip()

    @field_validator(DURABLE_NAME_FIELD, mode=BEFORE)
    def validate_durable_name(cls, value: JsonValue) -> JsonValue:
        """Validate ``durable_name``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The stripped durable name.

        Raises:
            SEDurableConsumerConfigInvalidDurableName: If the value is not a durable name.
        """
        if not isinstance(value, str) or not cls.NAME_PATTERN.match(value.strip()):
            raise SEDurableConsumerConfigInvalidDurableName(
                f"Invalid durable_name: {value!r}. Must be letters, digits, underscores and hyphens only."
            )
        return value.strip()

    @field_validator(FILTER_SUBJECT_FIELD, mode=BEFORE)
    def validate_filter_subject(cls, value: JsonValue) -> JsonValue:
        """Validate ``filter_subject``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The stripped subject, or ``None``.

        Raises:
            SEDurableConsumerConfigInvalidFilterSubject: If the value is not a well-formed subject.
        """
        if value is None:
            return None
        if not isinstance(value, str) or not cls.SUBJECT_PATTERN.match(value.strip()):
            raise SEDurableConsumerConfigInvalidFilterSubject(
                f"Invalid filter_subject: {value!r}. Must be dot-separated tokens, with no space and no empty token."
            )
        return value.strip()

    @field_validator(BATCH_SIZE_FIELD, mode=BEFORE)
    def validate_batch_size(cls, value: JsonValue) -> JsonValue:
        """Validate ``batch_size``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The batch size, or the default when ``None``.

        Raises:
            SEDurableConsumerConfigInvalidBatchSize: If the value is not an integer of at least the minimum.
        """
        if value is None:
            return cls.DEFAULT_BATCH_SIZE
        if isinstance(value, bool) or not isinstance(value, int) or value < cls.BATCH_SIZE_MIN:
            raise SEDurableConsumerConfigInvalidBatchSize(
                f"Invalid batch_size: {value!r}. Must be an integer of at least {cls.BATCH_SIZE_MIN}."
            )
        return value

    @field_validator(FETCH_TIMEOUT_FIELD, mode=BEFORE)
    def validate_fetch_timeout_s(cls, value: JsonValue) -> JsonValue:
        """Validate ``fetch_timeout_s``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The duration, or the default when ``None``.

        Raises:
            SEDurableConsumerConfigInvalidFetchTimeout: If the value is not a positive number.
        """
        if value is None:
            return cls.DEFAULT_FETCH_TIMEOUT_S
        if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
            raise SEDurableConsumerConfigInvalidFetchTimeout(
                f"Invalid fetch_timeout_s: {value!r}. Must be a positive number."
            )
        return value

    @field_validator(ACK_WAIT_FIELD, mode=BEFORE)
    def validate_ack_wait_s(cls, value: JsonValue) -> JsonValue:
        """Validate ``ack_wait_s``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The duration, or the default when ``None``.

        Raises:
            SEDurableConsumerConfigInvalidAckWait: If the value is not a positive number.
        """
        if value is None:
            return cls.DEFAULT_ACK_WAIT_S
        if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
            raise SEDurableConsumerConfigInvalidAckWait(f"Invalid ack_wait_s: {value!r}. Must be a positive number.")
        return value

    @field_validator(MAX_DELIVER_FIELD, mode=BEFORE)
    def validate_max_deliver(cls, value: JsonValue) -> JsonValue:
        """Validate ``max_deliver``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The delivery limit, or the default when ``None``.

        Raises:
            SEDurableConsumerConfigInvalidMaxDeliver: If the value is neither ``-1`` nor a positive integer.
        """
        if value is None:
            return cls.DEFAULT_MAX_DELIVER
        if (
            isinstance(value, bool)
            or not isinstance(value, int)
            or (value != cls.MAX_DELIVER_UNLIMITED and value < cls.MAX_DELIVER_MIN)
        ):
            raise SEDurableConsumerConfigInvalidMaxDeliver(
                f"Invalid max_deliver: {value!r}. "
                f"Must be {cls.MAX_DELIVER_UNLIMITED} for unlimited or an integer of at least {cls.MAX_DELIVER_MIN}."
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
            SEDurableConsumerConfigInvalidStatusInterval: If the value is not a positive number.
        """
        if value is None:
            return cls.DEFAULT_STATUS_INTERVAL_S
        if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
            raise SEDurableConsumerConfigInvalidStatusInterval(
                f"Invalid status_interval_s: {value!r}. Must be a positive number."
            )
        return value
