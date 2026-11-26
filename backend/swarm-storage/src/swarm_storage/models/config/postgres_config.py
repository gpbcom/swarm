from __future__ import annotations

# Standard library imports
import re
from typing import ClassVar, Literal, Pattern

# Third-party imports
from pydantic import BaseModel, ConfigDict, Field, JsonValue, field_validator, model_validator

# First-party imports
from swarm_storage.models.config.exceptions import (
    SEPostgresConfigInvalidCommandTimeout,
    SEPostgresConfigInvalidDsnKey,
    SEPostgresConfigInvalidPoolMaxSize,
    SEPostgresConfigInvalidPoolMinSize,
    SEPostgresConfigInvalidStatusInterval,
    SEPostgresConfigPoolSizesInverted,
)


class PostgresConfig(BaseModel):
    """The settings of a PostgreSQL connection pool.

    Attributes:
        dsn_key (str): The name of the environment entry that holds the DSN, never the DSN itself.
        pool_min_size (int): The fewest connections the pool keeps open.
        pool_max_size (int): The most connections the pool opens.
        command_timeout_s (float): How long a command may run, in seconds.
        status_interval_s (float): How often a long-running task yields its status, in seconds.
        DSN_KEY_FIELD (str): The name of the ``dsn_key`` field, for its validator.
        POOL_MIN_SIZE_FIELD (str): The name of the ``pool_min_size`` field, for its validator.
        POOL_MAX_SIZE_FIELD (str): The name of the ``pool_max_size`` field, for its validator.
        COMMAND_TIMEOUT_FIELD (str): The name of the ``command_timeout_s`` field, for its validator.
        STATUS_INTERVAL_FIELD (str): The name of the ``status_interval_s`` field, for its validator.
        DEFAULT_DSN_KEY (str): The default environment entry name.
        DEFAULT_POOL_MIN_SIZE (int): The default minimum pool size.
        DEFAULT_POOL_MAX_SIZE (int): The default maximum pool size.
        DEFAULT_COMMAND_TIMEOUT_S (float): The default command timeout.
        DEFAULT_STATUS_INTERVAL_S (float): The default status interval.
        POOL_MIN_SIZE_MIN (int): The smallest minimum pool size.
        POOL_MIN_SIZE_MAX (int): The largest minimum pool size.
        POOL_MAX_SIZE_MIN (int): The smallest maximum pool size.
        POOL_MAX_SIZE_MAX (int): The largest maximum pool size.
        DSN_KEY_PATTERN (Pattern[str]): Upper case letters, digits and underscores, starting with a letter.
        BEFORE (str): The validator mode that runs before Pydantic's own validation.
        AFTER (str): The validator mode that runs after Pydantic's own validation.

    Notes:
        - Pools are small because PgBouncer sits in front of PostgreSQL.
        - **A secret never appears here**: ``dsn_key`` only names the environment entry that holds the DSN.
        - A boolean is refused where a number is expected.
    """

    DSN_KEY_FIELD: ClassVar[str] = "dsn_key"
    POOL_MIN_SIZE_FIELD: ClassVar[str] = "pool_min_size"
    POOL_MAX_SIZE_FIELD: ClassVar[str] = "pool_max_size"
    COMMAND_TIMEOUT_FIELD: ClassVar[str] = "command_timeout_s"
    STATUS_INTERVAL_FIELD: ClassVar[str] = "status_interval_s"
    DEFAULT_DSN_KEY: ClassVar[str] = "SWARM_POSTGRES_DSN"
    DEFAULT_POOL_MIN_SIZE: ClassVar[int] = 1
    DEFAULT_POOL_MAX_SIZE: ClassVar[int] = 5
    DEFAULT_COMMAND_TIMEOUT_S: ClassVar[float] = 5.0
    DEFAULT_STATUS_INTERVAL_S: ClassVar[float] = 5.0
    POOL_MIN_SIZE_MIN: ClassVar[int] = 1
    POOL_MIN_SIZE_MAX: ClassVar[int] = 10
    POOL_MAX_SIZE_MIN: ClassVar[int] = 1
    POOL_MAX_SIZE_MAX: ClassVar[int] = 20
    DSN_KEY_PATTERN: ClassVar[Pattern[str]] = re.compile(r"^[A-Z][A-Z0-9_]*$")
    BEFORE: ClassVar[Literal["before"]] = "before"
    AFTER: ClassVar[Literal["after"]] = "after"

    model_config = ConfigDict(extra="forbid", validate_default=True)

    dsn_key: str = Field(
        default=DEFAULT_DSN_KEY,
        description="The environment entry that holds the DSN, never the DSN itself. Defaults to SWARM_POSTGRES_DSN.",
    )
    pool_min_size: int = Field(
        default=DEFAULT_POOL_MIN_SIZE,
        description="The fewest connections the pool keeps open, from 1 to 10. Defaults to 1.",
    )
    pool_max_size: int = Field(
        default=DEFAULT_POOL_MAX_SIZE,
        description="The most connections the pool opens, from 1 to 20. Defaults to 5.",
    )
    command_timeout_s: float = Field(
        default=DEFAULT_COMMAND_TIMEOUT_S,
        description="How long a command may run, in seconds. Defaults to 5.",
    )
    status_interval_s: float = Field(
        default=DEFAULT_STATUS_INTERVAL_S,
        description="How often a long-running task yields its status, in seconds. Defaults to 5.",
    )

    @field_validator(DSN_KEY_FIELD, mode=BEFORE)
    def validate_dsn_key(cls, value: JsonValue) -> JsonValue:
        """Validate ``dsn_key``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The stripped entry name, or the default when ``None``.

        Raises:
            SEPostgresConfigInvalidDsnKey: If the value is not an upper case environment entry name.
        """
        if value is None:
            return cls.DEFAULT_DSN_KEY
        if not isinstance(value, str) or not cls.DSN_KEY_PATTERN.match(value.strip()):
            raise SEPostgresConfigInvalidDsnKey(
                f"Invalid dsn_key: {value!r}. "
                "Must be upper case letters, digits and underscores, starting with a letter."
            )
        return value.strip()

    @field_validator(POOL_MIN_SIZE_FIELD, mode=BEFORE)
    def validate_pool_min_size(cls, value: JsonValue) -> JsonValue:
        """Validate ``pool_min_size``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The size, or the default when ``None``.

        Raises:
            SEPostgresConfigInvalidPoolMinSize: If the value is not an integer within the bounds.
        """
        if value is None:
            return cls.DEFAULT_POOL_MIN_SIZE
        if (
            isinstance(value, bool)
            or not isinstance(value, int)
            or not cls.POOL_MIN_SIZE_MIN <= value <= cls.POOL_MIN_SIZE_MAX
        ):
            raise SEPostgresConfigInvalidPoolMinSize(
                f"Invalid pool_min_size: {value!r}. "
                f"Must be an integer in [{cls.POOL_MIN_SIZE_MIN}, {cls.POOL_MIN_SIZE_MAX}]."
            )
        return value

    @field_validator(POOL_MAX_SIZE_FIELD, mode=BEFORE)
    def validate_pool_max_size(cls, value: JsonValue) -> JsonValue:
        """Validate ``pool_max_size``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The size, or the default when ``None``.

        Raises:
            SEPostgresConfigInvalidPoolMaxSize: If the value is not an integer within the bounds.
        """
        if value is None:
            return cls.DEFAULT_POOL_MAX_SIZE
        if (
            isinstance(value, bool)
            or not isinstance(value, int)
            or not cls.POOL_MAX_SIZE_MIN <= value <= cls.POOL_MAX_SIZE_MAX
        ):
            raise SEPostgresConfigInvalidPoolMaxSize(
                f"Invalid pool_max_size: {value!r}. "
                f"Must be an integer in [{cls.POOL_MAX_SIZE_MIN}, {cls.POOL_MAX_SIZE_MAX}]."
            )
        return value

    @field_validator(COMMAND_TIMEOUT_FIELD, mode=BEFORE)
    def validate_command_timeout_s(cls, value: JsonValue) -> JsonValue:
        """Validate ``command_timeout_s``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The duration, or the default when ``None``.

        Raises:
            SEPostgresConfigInvalidCommandTimeout: If the value is not a positive number.
        """
        if value is None:
            return cls.DEFAULT_COMMAND_TIMEOUT_S
        if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
            raise SEPostgresConfigInvalidCommandTimeout(
                f"Invalid command_timeout_s: {value!r}. Must be a positive number."
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
            SEPostgresConfigInvalidStatusInterval: If the value is not a positive number.
        """
        if value is None:
            return cls.DEFAULT_STATUS_INTERVAL_S
        if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
            raise SEPostgresConfigInvalidStatusInterval(
                f"Invalid status_interval_s: {value!r}. Must be a positive number."
            )
        return value

    @model_validator(mode=AFTER)
    def validate_pool_sizes(self) -> PostgresConfig:
        """Check that the minimum pool size does not exceed the maximum.

        Returns:
            PostgresConfig: This configuration.

        Raises:
            SEPostgresConfigPoolSizesInverted: If ``pool_min_size`` is greater than ``pool_max_size``.
        """
        if self.pool_min_size > self.pool_max_size:
            raise SEPostgresConfigPoolSizesInverted(
                f"Invalid pool sizes: {self.pool_min_size!r} and {self.pool_max_size!r}. "
                "The minimum must not exceed the maximum."
            )
        return self
