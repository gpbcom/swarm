from __future__ import annotations

# Standard library imports
from logging import Logger, getLogger
from pathlib import Path
from typing import Optional

# Third-party imports
from fastapi import FastAPI

# First-party imports
from swarm_lifecycle.factories.runnable_factory import RunnableFactory
from swarm_rest.api.cli.openapi_export_command import OpenApiExportCommand


class OpenApiExportCommandFactory(RunnableFactory[OpenApiExportCommand]):
    """Builds OpenAPI export commands.

    Attributes:
        app (FastAPI): The application whose document is exported.
        path (Path): The file written or checked.
        check (bool): Whether the commands compare instead of writing.
    """

    def __init__(self, app: FastAPI, path: Path, check: bool, logger: Optional[Logger] = None) -> None:
        """Initialise the factory.

        Args:
            app (FastAPI): The application whose document is exported.
            path (Path): The file written or checked.
            check (bool): Whether the commands compare instead of writing.
            logger (Optional[Logger]): Logger to use. A logger named after the module is used when it is ``None``.
        """
        super().__init__()
        self.logger = logger if logger else getLogger(__name__)
        self.app = app
        self.path = path
        self.check = check

    ############################
    # Internal Helpers Methods #
    ############################

    def _build(self) -> OpenApiExportCommand:
        """Build one command.

        Returns:
            OpenApiExportCommand: A new command with the factory's arguments.
        """
        self.logger.debug("Building an export command for %s.", self.path)
        return OpenApiExportCommand(self.app, self.path, self.check)
