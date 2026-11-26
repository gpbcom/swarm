from __future__ import annotations

# Standard library imports
import re
from io import StringIO
from logging import Logger, getLogger
from pathlib import Path
from typing import ClassVar, Optional, Pattern

# Third-party imports
from babel.messages.catalog import Catalog
from babel.messages.pofile import PoFileError, read_po

# First-party imports
from swarm_i18n.models.catalogs.exceptions import SECatalogUnreadableError  # isort: skip
from swarm_models.models.enums import Language


class PoCatalogStore:
    """Reads the Babel message catalogues of Swarm from disk.

    Attributes:
        DOMAIN (str): The gettext domain of the catalogues.
        DEFAULT_ROOT (Path): The ``locales`` folder shipped beside the package.
        ENCODING (str): The encoding of the catalogue files.
        TEMPLATE_SUFFIX (str): The suffix of the template file.
        CATALOG_SUFFIX (str): The suffix of a language catalogue file.
        MESSAGES_FOLDER (str): The gettext folder holding the catalogue of a language.
        READ_MODE (str): The mode in which catalogue files are opened.
        LINE_PATTERN (Pattern[str]): What a well-formed line of a catalogue looks like.
        LOCALES_FOLDER (str): The name of the folder of the shipped catalogues.
        root (Path): The folder holding the template and the language folders.
        logger (Logger): Logger instance.

    Notes:
        This class only reads data. Checking it is the job of the service layer.
    """

    DOMAIN: ClassVar[str] = "swarm"
    LOCALES_FOLDER: ClassVar[str] = "locales"
    DEFAULT_ROOT: ClassVar[Path] = Path(__file__).resolve().parents[2] / LOCALES_FOLDER
    ENCODING: ClassVar[str] = "utf-8"
    TEMPLATE_SUFFIX: ClassVar[str] = ".pot"
    CATALOG_SUFFIX: ClassVar[str] = ".po"
    MESSAGES_FOLDER: ClassVar[str] = "LC_MESSAGES"
    READ_MODE: ClassVar[str] = "rb"
    LINE_PATTERN: ClassVar[Pattern[str]] = re.compile(r'^(#.*|(msg[a-z_]+(\[\d+\])?\s+)?".*"|)$')

    def __init__(self, root: Path, logger: Optional[Logger] = None) -> None:
        self.root = root
        self.logger = logger if logger else getLogger(__name__)

    ############################
    # Internal Helpers Methods #
    ############################

    def _first_malformed_line(self, text: str) -> Optional[int]:
        """Find the first line that is not valid in a catalogue.

        Args:
            text (str): The content of the catalogue.

        Returns:
            Optional[int]: The number of the first malformed line, or None when every line is well formed.

        Notes:
            Babel accepts an unterminated string without a word, so the lines are checked here first.
        """
        for number, line in enumerate(text.splitlines(), start=1):
            if not self.LINE_PATTERN.match(line.strip()):
                self.logger.debug("Line %d does not match the catalogue syntax.", number)
                return number
        self.logger.debug("No malformed line found.")
        return None

    def _read(self, path: Path) -> Catalog:
        """Read one catalogue file.

        Args:
            path (Path): The file to read.

        Returns:
            Catalog: The parsed catalogue.

        Raises:
            SECatalogUnreadableError: When the file cannot be opened or parsed.
        """
        try:
            text = path.read_text(encoding=self.ENCODING)
            bad_line = self._first_malformed_line(text)
            if bad_line is not None:
                self.logger.debug("Line %d of the catalogue %s is malformed.", bad_line, path)
                raise ValueError(f"Malformed line {bad_line}.")
            self.logger.debug("Every line of the catalogue %s is well formed.", path)
            catalog = read_po(StringIO(text), abort_invalid=True)
        except (OSError, PoFileError, ValueError) as error:
            self.logger.error("Cannot read the catalogue %s: %s.", path, type(error).__name__)
            raise SECatalogUnreadableError(f"Cannot read the catalogue {str(path)!r}.") from error
        self.logger.debug("Read the catalogue %s.", path)
        return catalog

    ############################
    # Publicly Exposed Methods #
    ############################

    def template(self) -> Catalog:
        """Read the template catalogue.

        Returns:
            Catalog: The catalogue of every message id.
        """
        return self._read(self.root / f"{self.DOMAIN}{self.TEMPLATE_SUFFIX}")

    def catalog(self, language: Language) -> Catalog:
        """Read the catalogue of one language.

        Args:
            language (Language): The language to read.

        Returns:
            Catalog: The catalogue of that language.
        """
        return self._read(self.root / language.value / self.MESSAGES_FOLDER / f"{self.DOMAIN}{self.CATALOG_SUFFIX}")
