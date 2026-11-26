from __future__ import annotations

# Standard library imports
import json
from logging import Logger, getLogger
from pathlib import Path
from typing import ClassVar, Optional

# Third-party imports
from fastapi import FastAPI

# First-party imports
from swarm_lifecycle.runnables.runnable import Runnable


class OpenApiExportCommand(Runnable):
    """Writes the OpenAPI document of an application to a file, or checks that the file is up to date.

    Attributes:
        ENCODING (ClassVar[str]): The encoding of the file.
        EXIT_OK (ClassVar[int]): The exit code when the work succeeded.
        EXIT_DIFFERENT (ClassVar[int]): The exit code when ``check`` finds the file missing or different.
        INDENT (ClassVar[int]): The indentation of the document.
        app (FastAPI): The application whose document is exported.
        path (Path): The file written or checked.
        check (bool): Whether to compare instead of writing.
        exit_code (int): The exit code, read after ``execute``.

    Notes:
        - The document is sorted and indented, and ends with a newline, so that it only changes with the API.
    """

    ENCODING: ClassVar[str] = "utf-8"
    EXIT_OK: ClassVar[int] = 0
    EXIT_DIFFERENT: ClassVar[int] = 1
    INDENT: ClassVar[int] = 2

    def __init__(self, app: FastAPI, path: Path, check: bool, logger: Optional[Logger] = None) -> None:
        """Initialise the command.

        Args:
            app (FastAPI): The application whose document is exported.
            path (Path): The file written or checked.
            check (bool): Whether to compare instead of writing.
            logger (Optional[Logger]): Logger to use. A logger named after the module is used when it is ``None``.
        """
        super().__init__()
        self.logger = logger if logger else getLogger(__name__)
        self.app = app
        self.path = path
        self.check = check
        self.exit_code = self.EXIT_OK

    ############################
    # Publicly Exposed Methods #
    ############################

    def render(self) -> str:
        """Render the OpenAPI document.

        Returns:
            str: The document as indented, sorted JSON that ends with a newline.
        """
        return json.dumps(self.app.openapi(), indent=self.INDENT, sort_keys=True, ensure_ascii=False) + "\n"

    def initialize(self) -> None:
        """Acquire nothing: the command only needs its arguments."""
        self.logger.debug("Nothing to initialise.")

    def run(self) -> None:
        """Write the document, or compare it with the file when ``check`` is set."""
        rendered = self.render()
        if self.check:
            if not self.path.is_file():
                self.logger.warning("The file %s is missing.", self.path)
                print(f"{self.path} is missing.")
                self.exit_code = self.EXIT_DIFFERENT
            elif self.path.read_text(encoding=self.ENCODING) != rendered:
                self.logger.warning("The file %s is out of date.", self.path)
                print(f"{self.path} is out of date.")
                self.exit_code = self.EXIT_DIFFERENT
            else:
                self.logger.info("The file %s is up to date.", self.path)
                self.exit_code = self.EXIT_OK
            return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(rendered, encoding=self.ENCODING)
        self.logger.info("Wrote %s.", self.path)
        print(f"Wrote {self.path}.")
        self.exit_code = self.EXIT_OK

    def close(self) -> None:
        """Release nothing: the command holds no resource."""
        self.logger.debug("Nothing to close.")
