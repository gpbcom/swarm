from __future__ import annotations

# Standard library imports
from logging import Logger, getLogger
from pathlib import Path
from typing import Optional

# First-party imports
from swarm_models.schemas.exceptions import SESchemaUnreadableError, SESchemaUnwritableError


class SchemaFolder:
    """The folder that holds the exported JSON Schema files.

    Attributes:
        root (Path): The folder the files live in.
        logger (Logger): Logger instance.

    Notes:
        Files are UTF-8 and ``\\n`` line endings are written as they are, so that the bytes do not depend on the
        platform.
    """

    def __init__(self, root: Path, logger: Optional[Logger] = None) -> None:
        """Create a folder handle.

        Args:
            root (Path): The folder the files live in.
            logger (Optional[Logger]): Logger instance.
        """
        self.root = root
        self.logger = logger if logger else getLogger(__name__)

    ############################
    # Publicly Exposed Methods #
    ############################

    def path(self, name: str) -> Path:
        """Give the path of a file of the folder.

        Args:
            name (str): The file name.

        Returns:
            Path: The path under the root.
        """
        return self.root / name

    def read(self, name: str) -> Optional[str]:
        """Read one file.

        Args:
            name (str): The file name.

        Returns:
            Optional[str]: The text, or ``None`` when the file does not exist.

        Raises:
            SESchemaUnreadableError: When the file exists but cannot be read as UTF-8.
        """
        target = self.path(name)
        if not target.exists():
            self.logger.debug("Schema file %s does not exist, read as None.", name)
            return None
        try:
            with target.open("r", encoding="utf-8", newline="") as handle:
                text = handle.read()
        except (OSError, UnicodeDecodeError) as error:
            self.logger.error("Cannot read schema file %s: %s.", name, type(error).__name__)
            raise SESchemaUnreadableError(f"Cannot read the schema file {name!r}.") from error
        self.logger.debug("Read schema file %s.", name)
        return text

    def write(self, name: str, text: str) -> Path:
        """Write one file, creating the folders.

        Args:
            name (str): The file name.
            text (str): The text to write.

        Returns:
            Path: The path written.

        Raises:
            SESchemaUnwritableError: When the file cannot be written.
        """
        target = self.path(name)
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open("w", encoding="utf-8", newline="") as handle:
                handle.write(text)
        except OSError as error:
            self.logger.error("Cannot write schema file %s: %s.", name, type(error).__name__)
            raise SESchemaUnwritableError(f"Cannot write the schema file {name!r}.") from error
        self.logger.info("Wrote schema file %s.", name)
        return target
