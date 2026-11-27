from __future__ import annotations

# Standard library imports
import re
from functools import partial
from typing import ClassVar, Dict, Literal, Pattern, Type, Union

# Third-party imports
from pydantic import ConfigDict, Field, JsonValue, field_validator

# First-party imports
from swarm_models.auth.auth_config import AuthConfig
from swarm_models.config.app_config import AppConfig
from swarm_models.config.gateway.exceptions import (
    SEGatewayConfigInvalidOperators,
    SEGatewayConfigInvalidPostgres,
    SEGatewayConfigInvalidRest,
    SEGatewayConfigInvalidSchemaName,
    SEGatewayConfigUnreadable,
)
from swarm_models.config.gateway.operator_directory_config import OperatorDirectoryConfig
from swarm_models.config.postgres.postgres_config import PostgresConfig
from swarm_models.live.feed.live_config import LiveConfig
from swarm_web.models.config.rest_config import RestConfig
from swarm_web.models.config.signals_config import SignalsConfig


class GatewayConfig(AppConfig):
    """The configuration of the gateway app.

    Attributes:
        schema_name (str): The PostgreSQL schema the gateway reads and writes, and no other.
        postgres (PostgresConfig): The connection pool settings.
        rest (RestConfig): The REST server settings.
        auth (AuthConfig): The check of the tokens the gateway receives.
        live (LiveConfig): The live feed and the client sessions of ``/v1/live``.
        operators (OperatorDirectoryConfig): The Operator directory and its Keycloak admin calls.
        UNREADABLE (type[Exception]): The exception raised when the file cannot be read.
        SERVICE_NAME (str): The service name of the app's signals.
        signals (SignalsConfig): The settings of the app's signals, named after the app by default.
        DSN_KEY (str): The environment entry that holds the DSN of the gateway.
        DEFAULT_SCHEMA_NAME (str): The default schema.
        SCHEMA_NAME_FIELD (str): The name of the ``schema_name`` field.
        POSTGRES_FIELD (str): The name of the ``postgres`` field.
        REST_FIELD (str): The name of the ``rest`` field.
        AUTH_FIELD (str): The name of the ``auth`` field.
        LIVE_FIELD (str): The name of the ``live`` field.
        OPERATORS_FIELD (str): The name of the ``operators`` field.
        DEFAULT_ISSUER_URL (str): The issuer of the tokens when ``auth`` is not configured.
        SCHEMA_NAME_PATTERN (Pattern[str]): Lower case letters, digits and underscores, starting with a letter.
        BEFORE (str): The validator mode that runs before Pydantic's own validation.

    Notes:
        - **The DSN is never here**: ``postgres.dsn_key`` only names the environment entry that holds it.
        - A ``postgres`` mapping without ``dsn_key`` takes ``DSN_KEY``, so that the gateway never reads the entry of
          another service.
        - The folders of the app come from ``AppConfig``, whose ``APP_ROOT_KEY`` each image sets.
        - The nested sections are validated by their own models, and their errors are raised unchanged.
    """

    UNREADABLE: ClassVar[Type[Exception]] = SEGatewayConfigUnreadable
    SERVICE_NAME: ClassVar[str] = "swarm-gateway"
    DSN_KEY: ClassVar[str] = "SWARM_GATEWAY_POSTGRES_DSN"
    DEFAULT_SCHEMA_NAME: ClassVar[str] = "gateway"
    SCHEMA_NAME_FIELD: ClassVar[str] = "schema_name"
    POSTGRES_FIELD: ClassVar[str] = "postgres"
    REST_FIELD: ClassVar[str] = "rest"
    AUTH_FIELD: ClassVar[str] = "auth"
    LIVE_FIELD: ClassVar[str] = "live"
    OPERATORS_FIELD: ClassVar[str] = "operators"
    DEFAULT_ISSUER_URL: ClassVar[str] = "http://keycloak.global.svc.cluster.local:8080/realms/swarm"
    SCHEMA_NAME_PATTERN: ClassVar[Pattern[str]] = re.compile(r"^[a-z][a-z0-9_]*$")
    BEFORE: ClassVar[Literal["before"]] = "before"

    model_config = ConfigDict(extra="forbid", frozen=True, validate_default=True)

    signals: SignalsConfig = Field(
        default_factory=partial(SignalsConfig, service_name=SERVICE_NAME),
        description="The settings of the signals (traces, metrics and logs) the app exports, named after the app.",
    )
    schema_name: str = Field(
        default=DEFAULT_SCHEMA_NAME,
        description="The PostgreSQL schema the gateway reads and writes, and no other. Defaults to gateway.",
    )
    postgres: PostgresConfig = Field(
        default_factory=lambda: PostgresConfig(dsn_key=GatewayConfig.DSN_KEY),
        description="The connection pool settings. Its dsn_key defaults to SWARM_GATEWAY_POSTGRES_DSN.",
    )
    rest: RestConfig = Field(default_factory=RestConfig, description="The REST server settings.")
    auth: AuthConfig = Field(
        default_factory=lambda: AuthConfig(issuer_url=GatewayConfig.DEFAULT_ISSUER_URL),
        description="The check of the tokens the gateway receives. Its issuer_url defaults to the Keycloak service.",
    )

    live: LiveConfig = Field(
        default_factory=LiveConfig, description="The live feed and the client sessions of the /v1/live WebSocket."
    )
    operators: OperatorDirectoryConfig = Field(
        default_factory=OperatorDirectoryConfig, description="The Operator directory and its Keycloak admin calls."
    )

    @field_validator(SCHEMA_NAME_FIELD, mode=BEFORE)
    def validate_schema_name(cls, value: JsonValue) -> JsonValue:
        """Validate ``schema_name``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The stripped schema name, or the default when ``None``.

        Raises:
            SEGatewayConfigInvalidSchemaName: If the value is not a lower case identifier.
        """
        if value is None:
            return cls.DEFAULT_SCHEMA_NAME
        if not isinstance(value, str) or not cls.SCHEMA_NAME_PATTERN.match(value.strip()):
            raise SEGatewayConfigInvalidSchemaName(
                f"Invalid schema_name: {value!r}. "
                "Must be lower case letters, digits and underscores, starting with a letter."
            )
        return value.strip()

    @field_validator(POSTGRES_FIELD, mode=BEFORE)
    def validate_postgres(cls, value: Union[JsonValue, PostgresConfig]) -> Union[JsonValue, PostgresConfig]:
        """Validate ``postgres``.

        Args:
            value (Union[JsonValue, PostgresConfig]): The raw input.

        Returns:
            Union[JsonValue, PostgresConfig]: The section, with the gateway's ``dsn_key`` when it gives none, or the
                default section when ``None``.

        Raises:
            SEGatewayConfigInvalidPostgres: If the value is not a mapping.
        """
        if value is None:
            return cls.model_fields[cls.POSTGRES_FIELD].get_default(call_default_factory=True)
        if isinstance(value, PostgresConfig):
            return value
        if not isinstance(value, dict):
            raise SEGatewayConfigInvalidPostgres(f"Invalid postgres: {value!r}. Must be a mapping.")
        section: Dict[str, JsonValue] = {PostgresConfig.DSN_KEY_FIELD: cls.DSN_KEY}
        section.update(value)
        return section

    @field_validator(REST_FIELD, mode=BEFORE)
    def validate_rest(cls, value: Union[JsonValue, RestConfig]) -> Union[JsonValue, RestConfig]:
        """Validate ``rest``.

        Args:
            value (Union[JsonValue, RestConfig]): The raw input.

        Returns:
            Union[JsonValue, RestConfig]: The section, or the default section when ``None``.

        Raises:
            SEGatewayConfigInvalidRest: If the value is not a mapping.
        """
        if value is None:
            return cls.model_fields[cls.REST_FIELD].get_default(call_default_factory=True)
        if not isinstance(value, (dict, RestConfig)):
            raise SEGatewayConfigInvalidRest(f"Invalid rest: {value!r}. Must be a mapping.")
        return value

    @field_validator(AUTH_FIELD, mode=BEFORE)
    def validate_auth(cls, value: Union[JsonValue, AuthConfig]) -> Union[JsonValue, AuthConfig]:
        """Validate ``auth``.

        Args:
            value (Union[JsonValue, AuthConfig]): The raw input.

        Returns:
            Union[JsonValue, AuthConfig]: The section, or the default section when ``None``.
        """
        if value is None:
            return cls.model_fields[cls.AUTH_FIELD].get_default(call_default_factory=True)
        return value

    @field_validator(LIVE_FIELD, mode=BEFORE)
    def validate_live(cls, value: Union[JsonValue, LiveConfig]) -> Union[JsonValue, LiveConfig]:
        """Validate ``live``.

        Args:
            value (Union[JsonValue, LiveConfig]): The raw input.

        Returns:
            Union[JsonValue, LiveConfig]: The section, or the default section when ``None``.
        """
        if value is None:
            return cls.model_fields[cls.LIVE_FIELD].get_default(call_default_factory=True)
        return value

    @field_validator(OPERATORS_FIELD, mode=BEFORE)
    def validate_operators(
        cls, value: Union[JsonValue, OperatorDirectoryConfig]
    ) -> Union[JsonValue, OperatorDirectoryConfig]:
        """Validate ``operators``.

        Args:
            value (Union[JsonValue, OperatorDirectoryConfig]): The raw input.

        Returns:
            Union[JsonValue, OperatorDirectoryConfig]: The section, or the default section when ``None``.

        Raises:
            SEGatewayConfigInvalidOperators: If the value is not a mapping.
        """
        if value is None:
            return cls.model_fields[cls.OPERATORS_FIELD].get_default(call_default_factory=True)
        if not isinstance(value, (dict, OperatorDirectoryConfig)):
            raise SEGatewayConfigInvalidOperators(f"Invalid operators: {value!r}. Must be a mapping.")
        return value
