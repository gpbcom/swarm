from __future__ import annotations

# Standard library imports
import os
from pathlib import Path
from typing import ClassVar, Literal, Union

# Third-party imports
from pydantic import Field, JsonValue, field_validator

# First-party imports
from swarm_catalog.models.yaml_catalog import YamlCatalog
from swarm_models.config.exceptions import SEAppConfigInvalidSignals
from swarm_web.models.config.signals_config import SignalsConfig


class AppConfig(YamlCatalog):
    """The configuration of an app of ``backend/apps/``, read from ``conf/app.yaml`` in the app's folder.

    Attributes:
        APP_ROOT_KEY (str): The environment entry that names the folder of the app.
        CONF_FOLDER (str): The name of the folder of the configuration files, in the app's folder.
        APP_FILE (str): The name of the configuration file.
        LOGGER_FILE (str): The name of the logging configuration file.
        MIGRATIONS_FOLDER (str): The name of the folder of the Alembic migrations, in the app's folder.
        SIGNALS_FIELD (str): The name of the ``signals`` field.
        SERVICE_NAME (str): The service name of the default ``signals`` section of the app.
        BEFORE (str): The validator mode that runs before Pydantic's own validation.
        signals (SignalsConfig): The settings of the signals (traces, metrics and logs) the app exports.

    Notes:
        - **The app's folder is passed in, never found from the path of a module**: an installed package has no
          source tree, so each image sets ``APP_ROOT_KEY`` to the folder its ``COPY`` fills.
        - Without the entry, the folder is the current one, so that an app runs from ``backend/apps/<app>``.
        - A relative path of a configuration, such as a catalogue, is read in the folder of the app
          (``in_app_folder``), never in the folder of a module.
        - Each app sets ``SERVICE_NAME`` to its own name and declares ``signals`` again with a default that carries
          it, so that its defaults, and therefore its ``conf/app.yaml`` that writes every default out, name the app.
    """

    APP_ROOT_KEY: ClassVar[str] = "SWARM_APP_ROOT"
    CONF_FOLDER: ClassVar[str] = "conf"
    APP_FILE: ClassVar[str] = "app.yaml"
    LOGGER_FILE: ClassVar[str] = "logger.yaml"
    MIGRATIONS_FOLDER: ClassVar[str] = "migrations"
    SIGNALS_FIELD: ClassVar[str] = "signals"
    SERVICE_NAME: ClassVar[str] = SignalsConfig.DEFAULT_SERVICE_NAME
    BEFORE: ClassVar[Literal["before"]] = "before"

    signals: SignalsConfig = Field(
        default_factory=SignalsConfig,
        description="The settings of the signals (traces, metrics and logs) the app exports.",
    )

    @field_validator(SIGNALS_FIELD, mode=BEFORE)
    def validate_signals(cls, value: Union[JsonValue, SignalsConfig]) -> Union[JsonValue, SignalsConfig]:
        """Validate ``signals``.

        Args:
            value (Union[JsonValue, SignalsConfig]): The raw input.

        Returns:
            Union[JsonValue, SignalsConfig]: The section, or the default section of the app when ``None``.

        Raises:
            SEAppConfigInvalidSignals: If the value is neither a mapping nor a SignalsConfig.
        """
        if value is None:
            return cls.model_fields[cls.SIGNALS_FIELD].get_default(call_default_factory=True)
        if not isinstance(value, (dict, SignalsConfig)):
            raise SEAppConfigInvalidSignals(f"Invalid signals: {value!r}. Must be a mapping.")
        return value

    ############################
    # Publicly Exposed Methods #
    ############################

    @classmethod
    def app_folder(cls) -> Path:
        """Return the folder of the app.

        Returns:
            Path: The folder named by ``APP_ROOT_KEY`` when it is set, else the current folder.
        """
        root = os.environ.get(cls.APP_ROOT_KEY)
        if root and root.strip():
            return Path(root.strip())
        return Path.cwd()

    @classmethod
    def conf_folder(cls) -> Path:
        """Return the folder of the configuration files.

        Returns:
            Path: ``conf`` in the folder of the app.
        """
        return cls.app_folder() / cls.CONF_FOLDER

    @classmethod
    def in_app_folder(cls, path: str) -> Path:
        """Find a file that the configuration names, in the folder of the app.

        Args:
            path (str): The path as configured.

        Returns:
            Path: The path itself when it is absolute, else the path in the folder of the app.
        """
        return cls.app_folder() / path

    @classmethod
    def migrations_folder(cls) -> Path:
        """Return the folder of the Alembic migrations.

        Returns:
            Path: ``migrations`` in the folder of the app.
        """
        return cls.app_folder() / cls.MIGRATIONS_FOLDER
