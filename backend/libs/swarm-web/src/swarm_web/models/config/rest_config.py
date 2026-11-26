from __future__ import annotations

# Standard library imports
from typing import ClassVar, Literal

# Third-party imports
from pydantic import BaseModel, ConfigDict, Field, JsonValue, field_validator

# First-party imports
from swarm_rest.models.config.exceptions import (
    SERestConfigInvalidHost,
    SERestConfigInvalidIdempotencyMaxEntries,
    SERestConfigInvalidIdempotencyTtl,
    SERestConfigInvalidPort,
    SERestConfigInvalidStatusInterval,
)


class RestConfig(BaseModel):
    """The settings of the REST server and of its idempotency store.

    Attributes:
        model_config (ConfigDict): Forbids unknown keys and validates the defaults.
        HOST_FIELD (ClassVar[str]): The name of the ``host`` field.
        PORT_FIELD (ClassVar[str]): The name of the ``port`` field.
        STATUS_INTERVAL_FIELD (ClassVar[str]): The name of the ``status_interval_s`` field.
        IDEMPOTENCY_TTL_FIELD (ClassVar[str]): The name of the ``idempotency_ttl_s`` field.
        IDEMPOTENCY_MAX_ENTRIES_FIELD (ClassVar[str]): The name of the ``idempotency_max_entries`` field.
        DEFAULT_HOST (ClassVar[str]): The default address to listen on, every interface.
        DEFAULT_PORT (ClassVar[int]): The default port.
        DEFAULT_STATUS_INTERVAL_S (ClassVar[float]): The default status interval, in seconds.
        DEFAULT_IDEMPOTENCY_TTL_S (ClassVar[float]): The default time an idempotent answer is kept, one day.
        DEFAULT_IDEMPOTENCY_MAX_ENTRIES (ClassVar[int]): The default number of answers kept.
        PORT_MIN (ClassVar[int]): The lowest port.
        PORT_MAX (ClassVar[int]): The highest port.
        IDEMPOTENCY_MAX_ENTRIES_MIN (ClassVar[int]): The fewest answers kept.
        BEFORE (ClassVar[Literal["before"]]): The mode of the validators.
        host (str): The address the server listens on.
        port (int): The port the server listens on.
        status_interval_s (float): The interval of the server's status, in seconds.
        idempotency_ttl_s (float): How long an idempotent answer is kept, in seconds.
        idempotency_max_entries (int): How many idempotent answers are kept at most.
    """

    HOST_FIELD: ClassVar[str] = "host"
    PORT_FIELD: ClassVar[str] = "port"
    STATUS_INTERVAL_FIELD: ClassVar[str] = "status_interval_s"
    IDEMPOTENCY_TTL_FIELD: ClassVar[str] = "idempotency_ttl_s"
    IDEMPOTENCY_MAX_ENTRIES_FIELD: ClassVar[str] = "idempotency_max_entries"
    DEFAULT_HOST: ClassVar[str] = "0.0.0.0"
    DEFAULT_PORT: ClassVar[int] = 8000
    DEFAULT_STATUS_INTERVAL_S: ClassVar[float] = 5.0
    DEFAULT_IDEMPOTENCY_TTL_S: ClassVar[float] = 86400.0
    DEFAULT_IDEMPOTENCY_MAX_ENTRIES: ClassVar[int] = 10000
    PORT_MIN: ClassVar[int] = 1
    PORT_MAX: ClassVar[int] = 65535
    IDEMPOTENCY_MAX_ENTRIES_MIN: ClassVar[int] = 1
    BEFORE: ClassVar[Literal["before"]] = "before"

    model_config = ConfigDict(extra="forbid", validate_default=True)

    host: str = Field(default=DEFAULT_HOST, description="The address the server listens on.")
    port: int = Field(default=DEFAULT_PORT, description="The port the server listens on.")
    status_interval_s: float = Field(
        default=DEFAULT_STATUS_INTERVAL_S, description="The interval of the server's status, in seconds."
    )
    idempotency_ttl_s: float = Field(
        default=DEFAULT_IDEMPOTENCY_TTL_S, description="How long an idempotent answer is kept, in seconds."
    )
    idempotency_max_entries: int = Field(
        default=DEFAULT_IDEMPOTENCY_MAX_ENTRIES, description="How many idempotent answers are kept at most."
    )

    @field_validator(HOST_FIELD, mode=BEFORE)
    def validate_host(cls, value: JsonValue) -> JsonValue:
        """Validate ``host``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The stripped host, or the default when ``None``.

        Raises:
            SERestConfigInvalidHost: If the value is not a non-empty string without whitespace.
        """
        if value is None:
            return cls.DEFAULT_HOST
        if not isinstance(value, str) or not value.strip() or len(value.strip().split()) != 1:
            raise SERestConfigInvalidHost(f"Invalid host: {value!r}. Must be a non-empty string without whitespace.")
        return value.strip()

    @field_validator(PORT_FIELD, mode=BEFORE)
    def validate_port(cls, value: JsonValue) -> JsonValue:
        """Validate ``port``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The port, or the default when ``None``.

        Raises:
            SERestConfigInvalidPort: If the value is not an integer from ``PORT_MIN`` to ``PORT_MAX``.
        """
        if value is None:
            return cls.DEFAULT_PORT
        if isinstance(value, bool) or not isinstance(value, int) or not cls.PORT_MIN <= value <= cls.PORT_MAX:
            raise SERestConfigInvalidPort(
                f"Invalid port: {value!r}. Must be an integer in [{cls.PORT_MIN}, {cls.PORT_MAX}]."
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
            SERestConfigInvalidStatusInterval: If the value is not a positive number.
        """
        if value is None:
            return cls.DEFAULT_STATUS_INTERVAL_S
        if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
            raise SERestConfigInvalidStatusInterval(f"Invalid status_interval_s: {value!r}. Must be a positive number.")
        return value

    @field_validator(IDEMPOTENCY_TTL_FIELD, mode=BEFORE)
    def validate_idempotency_ttl_s(cls, value: JsonValue) -> JsonValue:
        """Validate ``idempotency_ttl_s``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The duration, or the default when ``None``.

        Raises:
            SERestConfigInvalidIdempotencyTtl: If the value is not a positive number.
        """
        if value is None:
            return cls.DEFAULT_IDEMPOTENCY_TTL_S
        if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
            raise SERestConfigInvalidIdempotencyTtl(f"Invalid idempotency_ttl_s: {value!r}. Must be a positive number.")
        return value

    @field_validator(IDEMPOTENCY_MAX_ENTRIES_FIELD, mode=BEFORE)
    def validate_idempotency_max_entries(cls, value: JsonValue) -> JsonValue:
        """Validate ``idempotency_max_entries``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The count, or the default when ``None``.

        Raises:
            SERestConfigInvalidIdempotencyMaxEntries: If the value is not an integer of at least
                ``IDEMPOTENCY_MAX_ENTRIES_MIN``.
        """
        if value is None:
            return cls.DEFAULT_IDEMPOTENCY_MAX_ENTRIES
        if isinstance(value, bool) or not isinstance(value, int) or value < cls.IDEMPOTENCY_MAX_ENTRIES_MIN:
            raise SERestConfigInvalidIdempotencyMaxEntries(
                f"Invalid idempotency_max_entries: {value!r}. "
                f"Must be an integer of at least {cls.IDEMPOTENCY_MAX_ENTRIES_MIN}."
            )
        return value
