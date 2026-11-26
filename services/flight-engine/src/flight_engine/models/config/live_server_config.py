from __future__ import annotations

# Standard library imports
from typing import ClassVar, Literal

# Third-party imports
from pydantic import BaseModel, ConfigDict, Field, JsonValue, field_validator

# First-party imports
from flight_engine.models.config.exceptions import (
    SELiveServerConfigInvalidHost,
    SELiveServerConfigInvalidPort,
    SELiveServerConfigInvalidStatusInterval,
)
from swarm_models.models.base.swarm_model import SwarmModel


class LiveServerConfig(BaseModel):
    """The settings of the HTTP server that streams the live frames.

    Attributes:
        host (str): The address the server listens on.
        port (int): The port the server listens on.
        status_interval_s (float): How often the server runnable yields its status, in seconds.
        HOST_FIELD (str): The name of the ``host`` field, for its validator.
        PORT_FIELD (str): The name of the ``port`` field, for its validator.
        STATUS_INTERVAL_FIELD (str): The name of the ``status_interval_s`` field, for its validator.
        PORT_MIN (int): The smallest port.
        PORT_MAX (int): The largest port.
        DEFAULT_HOST (str): The default address, the local machine only.
        DEFAULT_PORT (int): The default port.
        DEFAULT_STATUS_INTERVAL_S (float): The default status interval.
        BEFORE (str): The validator mode that runs before Pydantic's own validation.
    """

    model_config = ConfigDict(extra="forbid", frozen=True, validate_default=True)

    HOST_FIELD: ClassVar[str] = "host"
    PORT_FIELD: ClassVar[str] = "port"
    STATUS_INTERVAL_FIELD: ClassVar[str] = "status_interval_s"
    PORT_MIN: ClassVar[int] = 1
    PORT_MAX: ClassVar[int] = 65535
    DEFAULT_HOST: ClassVar[str] = "127.0.0.1"
    DEFAULT_PORT: ClassVar[int] = 8080
    DEFAULT_STATUS_INTERVAL_S: ClassVar[float] = 5.0
    BEFORE: ClassVar[Literal["before"]] = "before"

    host: str = Field(default=DEFAULT_HOST, description="The address the server listens on.")
    port: int = Field(default=DEFAULT_PORT, description="The port the server listens on, from 1 to 65535.")
    status_interval_s: float = Field(
        default=DEFAULT_STATUS_INTERVAL_S,
        description="How often the server yields its status, in seconds.",
    )

    @field_validator(HOST_FIELD, mode=BEFORE)
    def validate_host(cls, value: JsonValue) -> JsonValue:
        """Validate ``host``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The stripped address, or the default when ``None``.

        Raises:
            SELiveServerConfigInvalidHost: If the value is not a non-empty string.
        """
        if value is None:
            return cls.DEFAULT_HOST
        return SwarmModel.parse_text(cls.HOST_FIELD, value, SELiveServerConfigInvalidHost)

    @field_validator(PORT_FIELD, mode=BEFORE)
    def validate_port(cls, value: JsonValue) -> JsonValue:
        """Validate ``port``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The port, or the default when ``None``.

        Raises:
            SELiveServerConfigInvalidPort: If the value is not an integer from 1 to 65535.
        """
        if value is None:
            return cls.DEFAULT_PORT
        return SwarmModel.parse_int(cls.PORT_FIELD, value, SELiveServerConfigInvalidPort, cls.PORT_MIN, cls.PORT_MAX)

    @field_validator(STATUS_INTERVAL_FIELD, mode=BEFORE)
    def validate_status_interval_s(cls, value: JsonValue) -> JsonValue:
        """Validate ``status_interval_s``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The duration, or the default when ``None``.

        Raises:
            SELiveServerConfigInvalidStatusInterval: If the value is not a positive number.
        """
        if value is None:
            return cls.DEFAULT_STATUS_INTERVAL_S
        number = SwarmModel.parse_float(cls.STATUS_INTERVAL_FIELD, value, SELiveServerConfigInvalidStatusInterval)
        if number <= 0:
            raise SELiveServerConfigInvalidStatusInterval(
                f"Invalid {cls.STATUS_INTERVAL_FIELD}: {value!r}. Must be a positive number."
            )
        return number
