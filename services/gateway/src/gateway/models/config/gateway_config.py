from __future__ import annotations

# Standard library imports
import os
import re
from pathlib import Path
from typing import ClassVar, Dict, Literal, Pattern, Type, Union

# Third-party imports
from pydantic import ConfigDict, Field, JsonValue, field_validator

# First-party imports
from gateway.models.auth.auth_config import AuthConfig
from gateway.models.config.exceptions import (
    SEGatewayConfigInvalidPostgres,
    SEGatewayConfigInvalidRest,
    SEGatewayConfigInvalidSchemaName,
    SEGatewayConfigUnreadable,
)
from gateway.models.live.live_config import LiveConfig
from swarm_catalog.models.yaml_catalog import YamlCatalog
from swarm_models.config.postgres.postgres_config import PostgresConfig
from swarm_web.models.config.rest_config import RestConfig


class GatewayConfig(YamlCatalog):
    """The configuration of the gateway service.

    Attributes:
        schema_name (str): The PostgreSQL schema the gateway reads and writes, and no other.
        postgres (PostgresConfig): The connection pool settings.
        rest (RestConfig): The REST server settings.
        auth (AuthConfig): The check of the tokens the gateway receives.
        live (LiveConfig): The live feed and the client sessions of ``/v1/live``.
        UNREADABLE (type[Exception]): The exception raised when the file cannot be read.
        APP_FILE (str): The name of the configuration file.
        LOGGER_FILE (str): The name of the logging configuration file.
        CONF_FOLDER (str): The name of the folder of the configuration files, in the service folder.
        MIGRATIONS_FOLDER (str): The name of the folder of the migrations, in the service folder.
        DSN_KEY (str): The environment entry that holds the DSN of the gateway.
        DEFAULT_SCHEMA_NAME (str): The default schema.
        SCHEMA_NAME_FIELD (str): The name of the ``schema_name`` field.
        POSTGRES_FIELD (str): The name of the ``postgres`` field.
        REST_FIELD (str): The name of the ``rest`` field.
        AUTH_FIELD (str): The name of the ``auth`` field.
        LIVE_FIELD (str): The name of the ``live`` field.
        DEFAULT_ISSUER_URL (str): The issuer of the tokens when ``auth`` is not configured.
        SCHEMA_NAME_PATTERN (Pattern[str]): Lower case letters, digits and underscores, starting with a letter.
        HOME_KEY (str): The environment entry that names the service folder when the package is installed.
        SERVICE_FOLDER_DEPTH (int): How many folders separate this file from the service folder.
        BEFORE (str): The validator mode that runs before Pydantic's own validation.

    Notes:
        - **The DSN is never here**: ``postgres.dsn_key`` only names the environment entry that holds it.
        - A ``postgres`` mapping without ``dsn_key`` takes ``DSN_KEY``, so that the gateway never reads the entry of
          another service.
        - **An installed package has no source tree**: the images run ``uv sync --no-editable``, so the path of this
          file no longer leads to the service folder. ``HOME_KEY`` then names it, and each Dockerfile sets it to the
          folder its ``COPY`` fills.
        - The nested sections are validated by their own models, and their errors are raised unchanged.
    """

    UNREADABLE: ClassVar[Type[Exception]] = SEGatewayConfigUnreadable
    APP_FILE: ClassVar[str] = "app.yaml"
    LOGGER_FILE: ClassVar[str] = "logger.yaml"
    CONF_FOLDER: ClassVar[str] = "conf"
    MIGRATIONS_FOLDER: ClassVar[str] = "migrations"
    DSN_KEY: ClassVar[str] = "SWARM_GATEWAY_POSTGRES_DSN"
    DEFAULT_SCHEMA_NAME: ClassVar[str] = "gateway"
    SCHEMA_NAME_FIELD: ClassVar[str] = "schema_name"
    POSTGRES_FIELD: ClassVar[str] = "postgres"
    REST_FIELD: ClassVar[str] = "rest"
    AUTH_FIELD: ClassVar[str] = "auth"
    LIVE_FIELD: ClassVar[str] = "live"
    DEFAULT_ISSUER_URL: ClassVar[str] = "http://keycloak.global.svc.cluster.local:8080/realms/swarm"
    SCHEMA_NAME_PATTERN: ClassVar[Pattern[str]] = re.compile(r"^[a-z][a-z0-9_]*$")
    HOME_KEY: ClassVar[str] = "SWARM_GATEWAY_HOME"
    SERVICE_FOLDER_DEPTH: ClassVar[int] = 4
    BEFORE: ClassVar[Literal["before"]] = "before"

    model_config = ConfigDict(extra="forbid", frozen=True, validate_default=True)

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

    ############################
    # Publicly Exposed Methods #
    ############################

    @classmethod
    def service_folder(cls) -> Path:
        """Return the folder of the gateway service.

        Returns:
            Path: The folder named by ``HOME_KEY`` when it is set, else ``services/gateway``, found from this module's
                path.
        """
        home = os.environ.get(cls.HOME_KEY)
        if home and home.strip():
            return Path(home.strip())
        return Path(__file__).resolve().parents[cls.SERVICE_FOLDER_DEPTH]

    @classmethod
    def conf_folder(cls) -> Path:
        """Return the folder of the configuration files.

        Returns:
            Path: ``services/gateway/conf``.
        """
        return cls.service_folder() / cls.CONF_FOLDER

    @classmethod
    def migrations_folder(cls) -> Path:
        """Return the folder of the Alembic migrations.

        Returns:
            Path: ``services/gateway/migrations``.
        """
        return cls.service_folder() / cls.MIGRATIONS_FOLDER
