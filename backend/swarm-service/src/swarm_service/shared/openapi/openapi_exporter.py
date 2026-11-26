from __future__ import annotations

# Standard library imports
import json
from logging import Logger, getLogger
from pathlib import Path
from typing import ClassVar, Optional

# Third-party imports
from fastapi import FastAPI

# First-party imports
from swarm_storage.shared.schemas.schema_folder import SchemaFolder


class OpenApiExporter:
    """Render the OpenAPI document of an application, write it and detect a stale one.

    Attributes:
        SUFFIX (ClassVar[str]): The suffix of the document file.
        INDENT (ClassVar[int]): The indentation of the document.
        app (FastAPI): The application whose document is exported.
        name (str): The name of the document, the app's name, without its suffix.
        folder (SchemaFolder): The folder the document lives in.
        logger (Logger): Logger instance.

    Notes:
        - The document is sorted and indented, and ends with a newline, so that it only changes with the API and a
          stale file is detected by a plain comparison.
        - Storage errors propagate unchanged.
    """

    SUFFIX: ClassVar[str] = ".json"
    INDENT: ClassVar[int] = 2

    def __init__(self, app: FastAPI, root: Path, name: str, logger: Optional[Logger] = None) -> None:
        """Create an exporter.

        Args:
            app (FastAPI): The application whose document is exported.
            root (Path): The folder of the documents, ``frontend/packages/api-client/openapi`` in the repository.
            name (str): The name of the document, the app's name, without its suffix.
            logger (Optional[Logger]): Logger instance.
        """
        self.logger = logger if logger else getLogger(__name__)
        self.app = app
        self.name = name
        self.folder = SchemaFolder(root)

    ############################
    # Publicly Exposed Methods #
    ############################

    @property
    def file_name(self) -> str:
        """The name of the document file."""
        return self.name + self.SUFFIX

    @property
    def path(self) -> Path:
        """The path of the document file."""
        return self.folder.path(self.file_name)

    def render(self) -> str:
        """Render the OpenAPI document.

        Returns:
            str: The document as indented, sorted JSON that ends with a newline.
        """
        text = json.dumps(self.app.openapi(), indent=self.INDENT, sort_keys=True, ensure_ascii=False) + "\n"
        self.logger.debug("Rendered the OpenAPI document %s.", self.file_name)
        return text

    def export(self) -> Path:
        """Write the document.

        Returns:
            Path: The path written.
        """
        target = self.folder.write(self.file_name, self.render())
        self.logger.info("Exported the OpenAPI document to %s.", target)
        return target

    def is_stale(self) -> bool:
        """Tell whether the file on disk differs from the rendered document.

        Returns:
            bool: ``True`` when the file is missing or different.
        """
        if self.folder.read(self.file_name) == self.render():
            self.logger.debug("The OpenAPI document %s is current.", self.file_name)
            return False
        self.logger.warning("The OpenAPI document %s is stale.", self.file_name)
        return True
