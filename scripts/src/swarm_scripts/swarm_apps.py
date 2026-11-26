from __future__ import annotations

# Standard library imports
import os
from logging import Logger, getLogger
from pathlib import Path
from typing import Callable, ClassVar, Dict, List, Optional, Type, Union

# Third-party imports
from fastapi import FastAPI

# First-party imports
from swarm_api.v1.fleet.fleet_router import FleetRouter
from swarm_api.v1.gateway.gateway_router import GatewayRouter
from swarm_api.v1.missions.missions_router import MissionsRouter
from swarm_models.config.app_config import AppConfig
from swarm_models.config.fleet.fleet_config import FleetConfig
from swarm_models.config.gateway.gateway_config import GatewayConfig
from swarm_models.config.missions.missions_config import MissionsConfig
from swarm_models.enums import AppName
from swarm_scripts.repository_paths import RepositoryPaths


class SwarmApps:
    """The apps a script acts on: every app of ``backend/apps/``, or the one the environment names.

    Attributes:
        APP_KEY (ClassVar[str]): The environment entry that names the one app to act on.
        CONFIGS (ClassVar[Dict[AppName, Type[Union[GatewayConfig, FleetConfig, MissionsConfig]]]]): The configuration
            model of each app.
        APPLICATIONS (ClassVar[Dict[AppName, Callable[[], FastAPI]]]): Builds the FastAPI application of each app,
            with its default configuration.
        logger (Logger): Logger instance.

    Notes:
        - The scripts take no argument: ``SWARM_APP`` narrows them to one app, and ``SWARM_APP_ROOT`` then names its
          folder, as in its image. Without ``SWARM_APP``, the folder of each app is the repository's.
        - The application is built by the api layer, as the app's ``main()`` builds it, so that its OpenAPI document
          is the one the app serves.
    """

    APP_KEY: ClassVar[str] = "SWARM_APP"
    CONFIGS: ClassVar[Dict[AppName, Type[Union[GatewayConfig, FleetConfig, MissionsConfig]]]] = {
        AppName.GATEWAY: GatewayConfig,
        AppName.FLEET: FleetConfig,
        AppName.MISSIONS: MissionsConfig,
    }
    APPLICATIONS: ClassVar[Dict[AppName, Callable[[], FastAPI]]] = {
        AppName.GATEWAY: lambda: GatewayRouter(GatewayConfig()).application(),
        AppName.FLEET: lambda: FleetRouter(FleetConfig()).application(),
        AppName.MISSIONS: lambda: MissionsRouter(MissionsConfig()).application(),
    }

    def __init__(self, logger: Optional[Logger] = None) -> None:
        """Initialise the apps.

        Args:
            logger (Optional[Logger]): Logger instance.
        """
        self.logger = logger if logger else getLogger(__name__)

    ############################
    # Internal Helpers Methods #
    ############################

    def _entry(self, key: str) -> Optional[str]:
        """Read an environment entry.

        Args:
            key (str): The name of the entry.

        Returns:
            Optional[str]: The stripped value, or ``None`` when the entry is not set or blank.
        """
        value = os.environ.get(key)
        if value is None or not value.strip():
            self.logger.debug("The environment entry %s is not set.", key)
            return None
        return value.strip()

    ############################
    # Publicly Exposed Methods #
    ############################

    def requested(self) -> Optional[str]:
        """Read the app the environment names.

        Returns:
            Optional[str]: The stripped value of ``APP_KEY``, or ``None`` when it is not set or blank.
        """
        return self._entry(self.APP_KEY)

    def selected(self) -> List[AppName]:
        """List the apps to act on.

        Returns:
            List[AppName]: The app ``APP_KEY`` names, every app without it, or none when it names no app.
        """
        requested = self.requested()
        if requested is None:
            self.logger.debug("No app is named: every app is selected.")
            return list(AppName)
        selected = [app for app in AppName if app.value == requested]
        self.logger.debug("The environment names the app %r.", requested)
        return selected

    def folder(self, app: AppName) -> Path:
        """Find the folder of an app.

        Args:
            app (AppName): The app.

        Returns:
            Path: The folder ``SWARM_APP_ROOT`` names when ``APP_KEY`` names the app, else ``backend/apps/<app>``.
        """
        root = self._entry(AppConfig.APP_ROOT_KEY)
        if root is not None and self.requested() == app.value:
            self.logger.debug("The folder of the app %s is %s, from the environment.", app.value, root)
            return Path(root)
        self.logger.debug("The folder of the app %s is the repository's.", app.value)
        return RepositoryPaths.APPS / app.value

    def config(self, app: AppName) -> Union[GatewayConfig, FleetConfig, MissionsConfig]:
        """Load the configuration of an app from its folder.

        Args:
            app (AppName): The app.

        Returns:
            Union[GatewayConfig, FleetConfig, MissionsConfig]: The configuration read from ``conf/app.yaml``.

        Raises:
            Exception: The ``UNREADABLE`` exception of the configuration model when the file cannot be read.
        """
        return self.CONFIGS[app].load(self.folder(app) / AppConfig.CONF_FOLDER / AppConfig.APP_FILE)
