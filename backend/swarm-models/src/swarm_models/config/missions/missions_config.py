from __future__ import annotations

# Standard library imports
import os
import re
from pathlib import Path
from typing import ClassVar, Literal, Pattern

# Third-party imports
from pydantic import ConfigDict, Field, JsonValue, field_validator

# First-party imports
from missions.models.config.exceptions import (
    SEMissionsConfigInvalidPostgres,
    SEMissionsConfigInvalidRest,
    SEMissionsConfigInvalidSchemaName,
    SEMissionsConfigUnreadable,
)
from swarm_catalog.models.yaml_catalog import YamlCatalog
from swarm_models.config.postgres.postgres_config import PostgresConfig
from swarm_web.models.config.rest_config import RestConfig


class MissionsConfig(YamlCatalog):
    """The configuration of the missions service.

    Attributes:
        model_config (ConfigDict): Forbids unknown keys, freezes the model and validates the defaults.
        UNREADABLE (type[Exception]): The exception raised when the file cannot be read.
        APP_FILE (str): The name of the configuration file.
        LOGGER_FILE (str): The name of the logging file.
        CONF_FOLDER_NAME (str): The name of the folder that holds both files.
        DSN_KEY (str): The environment entry that holds the PostgreSQL DSN.
        DEFAULT_SCHEMA_NAME (str): The default PostgreSQL schema of the service.
        SCHEMA_NAME_FIELD (str): The name of the ``schema_name`` field.
        POSTGRES_FIELD (str): The name of the ``postgres`` field.
        REST_FIELD (str): The name of the ``rest`` field.
        SCHEMA_NAME_PATTERN (Pattern[str]): Lower case letters, digits and underscores, starting with a letter.
        SERVICE_ROOT_LEVEL (int): How many folders up the service folder is from this file.
        HOME_KEY (str): The environment entry that names the service folder when the package is installed.
        MIGRATIONS_FOLDER_NAME (str): The name of the folder of the migrations, in the service folder.
        BEFORE (Literal["before"]): The mode of the validators.
        schema_name (str): The PostgreSQL schema that holds the tables of the service.
        postgres (PostgresConfig): The PostgreSQL connection settings.
        rest (RestConfig): The REST server settings.

    Notes:
        - **An installed package has no source tree**: the images run ``uv sync --no-editable``, so ``HOME_KEY``
          names the service folder, and each Dockerfile sets it to the folder its ``COPY`` fills.
        - **The DSN is never here**: ``postgres.dsn_key`` only names the environment entry that holds it.
        - The errors of a nested model are not wrapped, so each keeps its own type.
    """

    UNREADABLE: ClassVar[type[Exception]] = SEMissionsConfigUnreadable
    APP_FILE: ClassVar[str] = "app.yaml"
    LOGGER_FILE: ClassVar[str] = "logger.yaml"
    CONF_FOLDER_NAME: ClassVar[str] = "conf"
    DSN_KEY: ClassVar[str] = "SWARM_MISSIONS_POSTGRES_DSN"
    DEFAULT_SCHEMA_NAME: ClassVar[str] = "missions"
    SCHEMA_NAME_FIELD: ClassVar[str] = "schema_name"
    POSTGRES_FIELD: ClassVar[str] = "postgres"
    REST_FIELD: ClassVar[str] = "rest"
    SCHEMA_NAME_PATTERN: ClassVar[Pattern[str]] = re.compile(r"^[a-z][a-z0-9_]*$")
    SERVICE_ROOT_LEVEL: ClassVar[int] = 4
    HOME_KEY: ClassVar[str] = "SWARM_MISSIONS_HOME"
    MIGRATIONS_FOLDER_NAME: ClassVar[str] = "migrations"
    BEFORE: ClassVar[Literal["before"]] = "before"

    model_config = ConfigDict(extra="forbid", frozen=True, validate_default=True)

    schema_name: str = Field(
        default=DEFAULT_SCHEMA_NAME, description="The PostgreSQL schema of the service. Defaults to missions."
    )
    postgres: PostgresConfig = Field(
        default_factory=lambda: PostgresConfig(dsn_key=MissionsConfig.DSN_KEY),
        description="The PostgreSQL connection settings.",
    )
    rest: RestConfig = Field(default_factory=RestConfig, description="The REST server settings.")

    @field_validator(SCHEMA_NAME_FIELD, mode=BEFORE)
    def validate_schema_name(cls, value: JsonValue) -> JsonValue:
        """Validate ``schema_name``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The stripped name, or the default when ``None``.

        Raises:
            SEMissionsConfigInvalidSchemaName: If the value is not a lower case identifier.
        """
        if value is None:
            return cls.DEFAULT_SCHEMA_NAME
        if isinstance(value, bool) or not isinstance(value, str) or not cls.SCHEMA_NAME_PATTERN.match(value.strip()):
            raise SEMissionsConfigInvalidSchemaName(
                f"Invalid schema_name: {value!r}. "
                "Must be lower case letters, digits and underscores, starting with a letter."
            )
        return value.strip()

    @field_validator(POSTGRES_FIELD, mode=BEFORE)
    def validate_postgres(cls, value: JsonValue) -> JsonValue:
        """Validate ``postgres``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The mapping or model, or the default when ``None``.

        Raises:
            SEMissionsConfigInvalidPostgres: If the value is not a mapping or a ``PostgresConfig``.
        """
        if value is None:
            return PostgresConfig(dsn_key=cls.DSN_KEY).model_dump()
        if not isinstance(value, (dict, PostgresConfig)):
            raise SEMissionsConfigInvalidPostgres(f"Invalid postgres: {value!r}. Must be a mapping.")
        return value

    @field_validator(REST_FIELD, mode=BEFORE)
    def validate_rest(cls, value: JsonValue) -> JsonValue:
        """Validate ``rest``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The mapping or model, or the default when ``None``.

        Raises:
            SEMissionsConfigInvalidRest: If the value is not a mapping or a ``RestConfig``.
        """
        if value is None:
            return RestConfig().model_dump()
        if not isinstance(value, (dict, RestConfig)):
            raise SEMissionsConfigInvalidRest(f"Invalid rest: {value!r}. Must be a mapping.")
        return value

    ############################
    # Publicly Exposed Methods #
    ############################

    @classmethod
    def service_folder(cls) -> Path:
        """Return the folder of the missions service.

        Returns:
            Path: The folder named by ``HOME_KEY`` when it is set and not blank, else ``services/missions``, found from
                this module's path.
        """
        home = os.environ.get(cls.HOME_KEY)
        if home and home.strip():
            return Path(home.strip())
        return Path(__file__).resolve().parents[cls.SERVICE_ROOT_LEVEL]

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
