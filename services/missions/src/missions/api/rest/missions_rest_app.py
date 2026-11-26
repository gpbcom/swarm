from __future__ import annotations

# Standard library imports
from logging import Logger, getLogger
from pathlib import Path
from typing import ClassVar, Optional

# Third-party imports
from fastapi import FastAPI

# First-party imports
from missions.models.config.missions_config import MissionsConfig
from swarm_rest.api.rest.rest_app_builder import RestAppBuilder


class MissionsRestApp:
    """The REST application of the missions service, served under ``/v1``.

    Attributes:
        TITLE (ClassVar[str]): The title of the API.
        VERSION (ClassVar[str]): The version of the API.
        OPENAPI_OUTPUT (ClassVar[str]): The published OpenAPI document, relative to the repository root.
        REPOSITORY_ROOT_LEVEL (ClassVar[int]): How many folders up the repository root is from this file.
        config (MissionsConfig): The settings of the service.
        logger (Logger): Logger instance.

    Notes:
        - No router is mounted yet: the routes of the service come with its own tickets.
        - **The published document is generated from this application**: run ``swarm-missions-openapi`` after any
          change to a route, because a test fails on a stale file.
    """

    TITLE: ClassVar[str] = "Swarm missions"
    VERSION: ClassVar[str] = "0.1.0"
    OPENAPI_OUTPUT: ClassVar[str] = "frontend/packages/api-client/openapi/missions.json"
    REPOSITORY_ROOT_LEVEL: ClassVar[int] = 6

    def __init__(self, config: MissionsConfig, logger: Optional[Logger] = None) -> None:
        """Initialise the application factory.

        Args:
            config (MissionsConfig): The settings of the service.
            logger (Optional[Logger]): Logger to use. A logger named after the module is used when it is ``None``.
        """
        self.config = config
        self.logger = logger if logger else getLogger(__name__)

    ############################
    # Publicly Exposed Methods #
    ############################

    @classmethod
    def output_path(cls) -> Path:
        """Find the published OpenAPI document.

        Returns:
            Path: The absolute path of the file, in the repository.
        """
        return Path(__file__).resolve().parents[cls.REPOSITORY_ROOT_LEVEL] / cls.OPENAPI_OUTPUT

    def build(self) -> FastAPI:
        """Build the application.

        Returns:
            FastAPI: The application, with the REST conventions of Swarm and no router yet.
        """
        self.logger.debug("Building the missions application.")
        return RestAppBuilder(self.config.rest).build(self.TITLE, self.VERSION, [])
