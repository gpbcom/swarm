from __future__ import annotations

# Standard library imports
import os
import re
from pathlib import Path
from typing import ClassVar, Literal, Pattern, Type, Union

# Third-party imports
from pydantic import ConfigDict, Field, JsonValue, field_validator

# First-party imports
from fleet.models.config.exceptions import (
    SEFleetConfigInvalidPostgres,
    SEFleetConfigInvalidRest,
    SEFleetConfigInvalidSchemaName,
    SEFleetConfigUnreadable,
)
from swarm_catalog.models.yaml_catalog import YamlCatalog
from swarm_models.config.postgres.postgres_config import PostgresConfig
from swarm_web.models.config.rest_config import RestConfig


class FleetConfig(YamlCatalog):
    """The configuration of the fleet service.

    Attributes:
        schema_name (str): The PostgreSQL schema that holds the tables of the service.
        postgres (PostgresConfig): The PostgreSQL pool settings, which name the environment entry of the DSN.
        rest (RestConfig): The settings of the REST server.
        UNREADABLE (type[Exception]): The exception raised when the file cannot be read.
        APP_FILE (str): The name of the configuration file, in the conf folder.
        LOGGER_FILE (str): The name of the logging file, in the conf folder.
        CONF_FOLDER_NAME (str): The name of the folder that holds both files, in the service folder.
        DSN_KEY (str): The environment entry that holds the DSN of the service.
        DEFAULT_SCHEMA_NAME (str): The default schema.
        DEFAULT_POSTGRES (PostgresConfig): The default pool settings, with the DSN entry of the service.
        SCHEMA_NAME_PATTERN (Pattern[str]): What a schema name must match.
        SCHEMA_NAME_FIELD (str): The name of the ``schema_name`` field.
        POSTGRES_FIELD (str): The name of the ``postgres`` field.
        REST_FIELD (str): The name of the ``rest`` field.
        HOME_KEY (str): The environment entry that names the service folder when the package is installed.
        MIGRATIONS_FOLDER_NAME (str): The name of the folder of the migrations, in the service folder.
        SERVICE_FOLDER_DEPTH (int): How many folders separate this file from the service folder.
        BEFORE (str): The validator mode that runs before Pydantic's own validation.

    Notes:
        - **An installed package has no source tree**: the images run ``uv sync --no-editable``, so ``HOME_KEY``
          names the service folder, and each Dockerfile sets it to the folder its ``COPY`` fills.
        - **The DSN is never configured here**: ``postgres.dsn_key`` only names the environment entry.
        - The nested sections are validated by their own models.
    """

    UNREADABLE: ClassVar[Type[Exception]] = SEFleetConfigUnreadable
    APP_FILE: ClassVar[str] = "app.yaml"
    LOGGER_FILE: ClassVar[str] = "logger.yaml"
    CONF_FOLDER_NAME: ClassVar[str] = "conf"
    DSN_KEY: ClassVar[str] = "SWARM_FLEET_POSTGRES_DSN"
    DEFAULT_SCHEMA_NAME: ClassVar[str] = "fleet"
    DEFAULT_POSTGRES: ClassVar[PostgresConfig] = PostgresConfig(dsn_key=DSN_KEY)
    SCHEMA_NAME_PATTERN: ClassVar[Pattern[str]] = re.compile(r"^[a-z_][a-z0-9_]*$")
    SCHEMA_NAME_FIELD: ClassVar[str] = "schema_name"
    POSTGRES_FIELD: ClassVar[str] = "postgres"
    REST_FIELD: ClassVar[str] = "rest"
    HOME_KEY: ClassVar[str] = "SWARM_FLEET_HOME"
    MIGRATIONS_FOLDER_NAME: ClassVar[str] = "migrations"
    SERVICE_FOLDER_DEPTH: ClassVar[int] = 4
    BEFORE: ClassVar[Literal["before"]] = "before"

    model_config = ConfigDict(validate_default=True)

    schema_name: str = Field(
        default=DEFAULT_SCHEMA_NAME, description="The PostgreSQL schema of the service. Defaults to fleet."
    )
    postgres: PostgresConfig = Field(
        default=DEFAULT_POSTGRES, description="The PostgreSQL pool settings, with the DSN entry of the service."
    )
    rest: RestConfig = Field(default_factory=RestConfig, description="The settings of the REST server.")

    @field_validator(SCHEMA_NAME_FIELD, mode=BEFORE)
    def validate_schema_name(cls, value: JsonValue) -> JsonValue:
        """Validate ``schema_name``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The stripped name, or the default when ``None``.

        Raises:
            SEFleetConfigInvalidSchemaName: If the value is not a lower case identifier.
        """
        if value is None:
            return cls.DEFAULT_SCHEMA_NAME
        if not isinstance(value, str) or not cls.SCHEMA_NAME_PATTERN.match(value.strip()):
            raise SEFleetConfigInvalidSchemaName(
                f"Invalid schema_name: {value!r}. Must be a lower case identifier of letters, digits and underscores."
            )
        return value.strip()

    @field_validator(POSTGRES_FIELD, mode=BEFORE)
    def validate_postgres(cls, value: Union[JsonValue, PostgresConfig]) -> Union[JsonValue, PostgresConfig]:
        """Validate ``postgres``.

        Args:
            value (Union[JsonValue, PostgresConfig]): The raw input.

        Returns:
            Union[JsonValue, PostgresConfig]: The section, or the default section when ``None``.

        Raises:
            SEFleetConfigInvalidPostgres: If the value is neither a mapping nor a PostgresConfig.
        """
        if value is None:
            return cls.model_fields[cls.POSTGRES_FIELD].get_default(call_default_factory=True)
        if not isinstance(value, (dict, PostgresConfig)):
            raise SEFleetConfigInvalidPostgres(f"Invalid postgres: {type(value).__name__}. Must be a mapping.")
        return value

    @field_validator(REST_FIELD, mode=BEFORE)
    def validate_rest(cls, value: Union[JsonValue, RestConfig]) -> Union[JsonValue, RestConfig]:
        """Validate ``rest``.

        Args:
            value (Union[JsonValue, RestConfig]): The raw input.

        Returns:
            Union[JsonValue, RestConfig]: The section, or the default section when ``None``.

        Raises:
            SEFleetConfigInvalidRest: If the value is neither a mapping nor a RestConfig.
        """
        if value is None:
            return cls.model_fields[cls.REST_FIELD].get_default(call_default_factory=True)
        if not isinstance(value, (dict, RestConfig)):
            raise SEFleetConfigInvalidRest(f"Invalid rest: {type(value).__name__}. Must be a mapping.")
        return value

    ############################
    # Publicly Exposed Methods #
    ############################

    @classmethod
    def service_folder(cls) -> Path:
        """Return the folder of the fleet service.

        Returns:
            Path: The folder named by ``HOME_KEY`` when it is set and not blank, else ``services/fleet``, found from
                this module's path.
        """
        home = os.environ.get(cls.HOME_KEY)
        if home and home.strip():
            return Path(home.strip())
        return Path(__file__).resolve().parents[cls.SERVICE_FOLDER_DEPTH]

    @classmethod
    def conf_folder(cls) -> Path:
        """Find the ``conf`` folder of the service.

        Returns:
            Path: The folder that holds ``app.yaml`` and ``logger.yaml``.
        """
        return cls.service_folder() / cls.CONF_FOLDER_NAME

    @classmethod
    def migrations_folder(cls) -> Path:
        """Return the folder of the Alembic migrations.

        Returns:
            Path: The ``migrations`` folder of the service folder.
        """
        return cls.service_folder() / cls.MIGRATIONS_FOLDER_NAME
