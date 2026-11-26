from __future__ import annotations

# Standard library imports
import os
from pathlib import Path
from typing import ClassVar

# First-party imports
from swarm_catalog.models.yaml_catalog import YamlCatalog


class AppConfig(YamlCatalog):
    """The configuration of an app of ``backend/apps/``, read from ``conf/app.yaml`` in the app's folder.

    Attributes:
        APP_ROOT_KEY (str): The environment entry that names the folder of the app.
        CONF_FOLDER (str): The name of the folder of the configuration files, in the app's folder.
        APP_FILE (str): The name of the configuration file.
        LOGGER_FILE (str): The name of the logging configuration file.
        MIGRATIONS_FOLDER (str): The name of the folder of the Alembic migrations, in the app's folder.

    Notes:
        - **The app's folder is passed in, never found from the path of a module**: an installed package has no
          source tree, so each image sets ``APP_ROOT_KEY`` to the folder its ``COPY`` fills.
        - Without the entry, the folder is the current one, so that an app runs from ``backend/apps/<app>``.
        - A relative path of a configuration, such as a catalogue, is read in the folder of the app
          (``in_app_folder``), never in the folder of a module.
    """

    APP_ROOT_KEY: ClassVar[str] = "SWARM_APP_ROOT"
    CONF_FOLDER: ClassVar[str] = "conf"
    APP_FILE: ClassVar[str] = "app.yaml"
    LOGGER_FILE: ClassVar[str] = "logger.yaml"
    MIGRATIONS_FOLDER: ClassVar[str] = "migrations"

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
