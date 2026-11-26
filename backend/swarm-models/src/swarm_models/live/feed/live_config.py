from __future__ import annotations

# Standard library imports
from typing import ClassVar, Literal, Union

# Third-party imports
from pydantic import BaseModel, ConfigDict, Field, JsonValue, field_validator

# First-party imports
from swarm_models.live.feed.exceptions import (
    SELiveConfigInvalidNats,
    SELiveConfigInvalidSession,
    SELiveConfigInvalidStatusInterval,
)
from swarm_models.live.session.live_session_config import LiveSessionConfig
from swarm_nats.models.config.nats_client_config import NatsClientConfig


class LiveConfig(BaseModel):
    """The configuration of the live feed of the gateway.

    Attributes:
        status_interval_s (float): How often the live feed yields its status, in seconds.
        nats (NatsClientConfig): The connection to NATS, where the mission frames are published.
        session (LiveSessionConfig): The settings of each client session.
        STATUS_INTERVAL_FIELD (str): The name of the ``status_interval_s`` field.
        NATS_FIELD (str): The name of the ``nats`` field.
        SESSION_FIELD (str): The name of the ``session`` field.
        DEFAULT_STATUS_INTERVAL_S (float): The default status interval.
        BEFORE (str): The validator mode that runs before Pydantic's own validation.

    Notes:
        - The nested sections are validated by their own models, and their errors are raised unchanged.
        - A boolean is refused where a number is expected.
    """

    STATUS_INTERVAL_FIELD: ClassVar[str] = "status_interval_s"
    NATS_FIELD: ClassVar[str] = "nats"
    SESSION_FIELD: ClassVar[str] = "session"
    DEFAULT_STATUS_INTERVAL_S: ClassVar[float] = 5.0
    BEFORE: ClassVar[Literal["before"]] = "before"

    model_config = ConfigDict(extra="forbid", frozen=True, validate_default=True)

    status_interval_s: float = Field(
        default=DEFAULT_STATUS_INTERVAL_S,
        description="How often the live feed yields its status, in seconds. Defaults to 5.",
    )
    nats: NatsClientConfig = Field(
        default_factory=NatsClientConfig, description="The connection to NATS. Defaults to a local NATS."
    )
    session: LiveSessionConfig = Field(
        default_factory=LiveSessionConfig, description="The settings of each client session."
    )

    @field_validator(STATUS_INTERVAL_FIELD, mode=BEFORE)
    def validate_status_interval_s(cls, value: JsonValue) -> JsonValue:
        """Validate ``status_interval_s``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The duration, or the default when ``None``.

        Raises:
            SELiveConfigInvalidStatusInterval: If the value is not a positive number.
        """
        if value is None:
            return cls.DEFAULT_STATUS_INTERVAL_S
        if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
            raise SELiveConfigInvalidStatusInterval(f"Invalid status_interval_s: {value!r}. Must be a positive number.")
        return value

    @field_validator(NATS_FIELD, mode=BEFORE)
    def validate_nats(cls, value: Union[JsonValue, NatsClientConfig]) -> Union[JsonValue, NatsClientConfig]:
        """Validate ``nats``.

        Args:
            value (Union[JsonValue, NatsClientConfig]): The raw input.

        Returns:
            Union[JsonValue, NatsClientConfig]: The section, or the default section when ``None``.

        Raises:
            SELiveConfigInvalidNats: If the value is not a mapping.
        """
        if value is None:
            return cls.model_fields[cls.NATS_FIELD].get_default(call_default_factory=True)
        if not isinstance(value, (dict, NatsClientConfig)):
            raise SELiveConfigInvalidNats(f"Invalid nats: {value!r}. Must be a mapping.")
        return value

    @field_validator(SESSION_FIELD, mode=BEFORE)
    def validate_session(cls, value: Union[JsonValue, LiveSessionConfig]) -> Union[JsonValue, LiveSessionConfig]:
        """Validate ``session``.

        Args:
            value (Union[JsonValue, LiveSessionConfig]): The raw input.

        Returns:
            Union[JsonValue, LiveSessionConfig]: The section, or the default section when ``None``.

        Raises:
            SELiveConfigInvalidSession: If the value is not a mapping.
        """
        if value is None:
            return cls.model_fields[cls.SESSION_FIELD].get_default(call_default_factory=True)
        if not isinstance(value, (dict, LiveSessionConfig)):
            raise SELiveConfigInvalidSession(f"Invalid session: {value!r}. Must be a mapping.")
        return value
