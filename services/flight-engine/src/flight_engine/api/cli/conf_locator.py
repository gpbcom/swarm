from __future__ import annotations

# Standard library imports
from logging import Logger, getLogger
from pathlib import Path
from typing import ClassVar, Optional


class ConfLocator:
    """Finds a configuration file given relative to the folder the service starts in.

    Attributes:
        SERVICE_FOLDER_DEPTH (ClassVar[int]): How many parents up from this file the service folder is.
        logger (Logger): Logger instance.

    Notes:
        - A relative path is first tried from the current folder, as in the image, where the service starts in
          ``/app``.
        - **Otherwise it is tried from the service folder**, so that the service runs from any folder in a checkout.
    """

    SERVICE_FOLDER_DEPTH: ClassVar[int] = 4

    def __init__(self, logger: Optional[Logger] = None) -> None:
        """Initialise the locator.

        Args:
            logger (Optional[Logger]): Logger instance.
        """
        self.logger = logger if logger else getLogger(__name__)

    ############################
    # Publicly Exposed Methods #
    ############################

    def locate(self, path: Path) -> Path:
        """Find a file.

        Args:
            path (Path): The path as configured.

        Returns:
            Path: The path itself when it exists or is found nowhere else, otherwise the file in the service folder.
        """
        if path.exists():
            self.logger.debug("Using %s as it is.", path)
            return path
        candidate = Path(__file__).resolve().parents[self.SERVICE_FOLDER_DEPTH] / path
        if not path.is_absolute() and candidate.exists():
            self.logger.debug("Using %s from the service folder.", path)
            return candidate
        self.logger.debug("Found no other place for %s.", path)
        return path
