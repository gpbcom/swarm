from __future__ import annotations

# Standard library imports
import re
from typing import ClassVar, List, Literal, Optional, Pattern

# Third-party imports
from pydantic import BaseModel, ConfigDict, Field, JsonValue, field_validator

# First-party imports
from swarm_nats.models.config.exceptions import (
    SENatsClientConfigInvalidConnectTimeout,
    SENatsClientConfigInvalidCredentialsPath,
    SENatsClientConfigInvalidName,
    SENatsClientConfigInvalidReconnectWait,
    SENatsClientConfigInvalidRequestDeadline,
    SENatsClientConfigInvalidServers,
)


class NatsClientConfig(BaseModel):
    """The settings of a connection to NATS.

    Attributes:
        servers (List[str]): The server URLs, each ``nats://`` or ``tls://``, to connect to.
        name (str): The name this client gives to its connection.
        credentials_path (Optional[str]): The path of the credentials file, or ``None`` for none.
        connect_timeout_s (float): How long one connection attempt may last, in seconds.
        reconnect_wait_s (float): How long to wait between two reconnection attempts, in seconds.
        request_deadline_s (float): How long a request waits for its reply, in seconds.
        SERVERS_FIELD (str): The name of the ``servers`` field, for its validator.
        NAME_FIELD (str): The name of the ``name`` field, for its validator and its default.
        CREDENTIALS_PATH_FIELD (str): The name of the ``credentials_path`` field, for its validator.
        CONNECT_TIMEOUT_FIELD (str): The name of the ``connect_timeout_s`` field, for its validator.
        RECONNECT_WAIT_FIELD (str): The name of the ``reconnect_wait_s`` field, for its validator.
        REQUEST_DEADLINE_FIELD (str): The name of the ``request_deadline_s`` field, for its validator.
        DEFAULT_SERVERS (List[str]): The default server URLs, a local NATS.
        DEFAULT_NAME (str): The default connection name.
        DEFAULT_CONNECT_TIMEOUT_S (float): The default connection timeout, 2 s as in NATS clients.
        DEFAULT_RECONNECT_WAIT_S (float): The default wait between reconnections, 2 s as in NATS clients.
        DEFAULT_REQUEST_DEADLINE_S (float): The default deadline of a request.
        SERVER_PATTERN (Pattern[str]): What a server URL looks like: a scheme, a host and an optional port.
        BEFORE (str): The validator mode that runs before Pydantic's own validation.

    Notes:
        - ``credentials_path`` names a file and never holds a secret.
        - Every timing is a positive number of seconds.
    """

    SERVERS_FIELD: ClassVar[str] = "servers"
    NAME_FIELD: ClassVar[str] = "name"
    CREDENTIALS_PATH_FIELD: ClassVar[str] = "credentials_path"
    CONNECT_TIMEOUT_FIELD: ClassVar[str] = "connect_timeout_s"
    RECONNECT_WAIT_FIELD: ClassVar[str] = "reconnect_wait_s"
    REQUEST_DEADLINE_FIELD: ClassVar[str] = "request_deadline_s"
    DEFAULT_SERVERS: ClassVar[List[str]] = ["nats://127.0.0.1:4222"]
    DEFAULT_NAME: ClassVar[str] = "swarm"
    DEFAULT_CONNECT_TIMEOUT_S: ClassVar[float] = 2.0
    DEFAULT_RECONNECT_WAIT_S: ClassVar[float] = 2.0
    DEFAULT_REQUEST_DEADLINE_S: ClassVar[float] = 5.0
    SERVER_PATTERN: ClassVar[Pattern[str]] = re.compile(r"^(nats|tls)://[^\s/:]+(:\d+)?$")
    BEFORE: ClassVar[Literal["before"]] = "before"

    model_config = ConfigDict(extra="forbid", validate_default=True)

    servers: List[str] = Field(
        default=DEFAULT_SERVERS,
        description="The server URLs, each nats:// or tls://. Defaults to a local NATS.",
    )
    name: str = Field(default=DEFAULT_NAME, description="The name of the connection. Defaults to swarm.")
    credentials_path: Optional[str] = Field(
        default=None,
        description="The path of the credentials file. It names a file and never holds a secret. Defaults to none.",
    )
    connect_timeout_s: float = Field(
        default=DEFAULT_CONNECT_TIMEOUT_S,
        description="How long one connection attempt may last, in seconds. Defaults to 2.",
    )
    reconnect_wait_s: float = Field(
        default=DEFAULT_RECONNECT_WAIT_S,
        description="How long to wait between two reconnection attempts, in seconds. Defaults to 2.",
    )
    request_deadline_s: float = Field(
        default=DEFAULT_REQUEST_DEADLINE_S,
        description="How long a request waits for its reply, in seconds. Defaults to 5.",
    )

    @field_validator(SERVERS_FIELD, mode=BEFORE)
    def validate_servers(cls, value: JsonValue) -> JsonValue:
        """Validate ``servers``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The stripped server URLs, or the default when ``None``.

        Raises:
            SENatsClientConfigInvalidServers: If the value is not a non-empty list of server URLs.
        """
        if value is None:
            return list(cls.DEFAULT_SERVERS)
        if not isinstance(value, list) or not value:
            raise SENatsClientConfigInvalidServers(
                f"Invalid servers: {value!r}. Must be a non-empty list of server URLs."
            )
        servers: List[JsonValue] = []
        for server in value:
            if not isinstance(server, str) or not cls.SERVER_PATTERN.match(server.strip()):
                raise SENatsClientConfigInvalidServers(
                    f"Invalid servers: {value!r}. "
                    "Each server must be a nats:// or tls:// URL with a host and an optional port."
                )
            servers.append(server.strip())
        return servers

    @field_validator(NAME_FIELD, mode=BEFORE)
    def validate_name(cls, value: JsonValue) -> JsonValue:
        """Validate ``name``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The stripped name, or the default when ``None``.

        Raises:
            SENatsClientConfigInvalidName: If the value is not a non-empty string.
        """
        if value is None:
            return cls.model_fields[cls.NAME_FIELD].get_default(call_default_factory=True)
        if not isinstance(value, str) or not value.strip():
            raise SENatsClientConfigInvalidName(f"Invalid name: {value!r}. Must be a non-empty string.")
        return value.strip()

    @field_validator(CREDENTIALS_PATH_FIELD, mode=BEFORE)
    def validate_credentials_path(cls, value: JsonValue) -> JsonValue:
        """Validate ``credentials_path``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The stripped path, or ``None``.

        Raises:
            SENatsClientConfigInvalidCredentialsPath: If the value is not a non-empty string.
        """
        if value is None:
            return None
        if not isinstance(value, str) or not value.strip():
            raise SENatsClientConfigInvalidCredentialsPath(
                f"Invalid credentials_path: {value!r}. Must be a non-empty string."
            )
        return value.strip()

    @field_validator(CONNECT_TIMEOUT_FIELD, mode=BEFORE)
    def validate_connect_timeout_s(cls, value: JsonValue) -> JsonValue:
        """Validate ``connect_timeout_s``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The duration, or the default when ``None``.

        Raises:
            SENatsClientConfigInvalidConnectTimeout: If the value is not a positive number.
        """
        if value is None:
            return cls.DEFAULT_CONNECT_TIMEOUT_S
        if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
            raise SENatsClientConfigInvalidConnectTimeout(
                f"Invalid connect_timeout_s: {value!r}. Must be a positive number."
            )
        return value

    @field_validator(RECONNECT_WAIT_FIELD, mode=BEFORE)
    def validate_reconnect_wait_s(cls, value: JsonValue) -> JsonValue:
        """Validate ``reconnect_wait_s``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The duration, or the default when ``None``.

        Raises:
            SENatsClientConfigInvalidReconnectWait: If the value is not a positive number.
        """
        if value is None:
            return cls.DEFAULT_RECONNECT_WAIT_S
        if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
            raise SENatsClientConfigInvalidReconnectWait(
                f"Invalid reconnect_wait_s: {value!r}. Must be a positive number."
            )
        return value

    @field_validator(REQUEST_DEADLINE_FIELD, mode=BEFORE)
    def validate_request_deadline_s(cls, value: JsonValue) -> JsonValue:
        """Validate ``request_deadline_s``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The duration, or the default when ``None``.

        Raises:
            SENatsClientConfigInvalidRequestDeadline: If the value is not a positive number.
        """
        if value is None:
            return cls.DEFAULT_REQUEST_DEADLINE_S
        if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
            raise SENatsClientConfigInvalidRequestDeadline(
                f"Invalid request_deadline_s: {value!r}. Must be a positive number."
            )
        return value
