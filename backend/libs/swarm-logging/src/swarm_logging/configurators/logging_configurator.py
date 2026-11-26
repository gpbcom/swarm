from __future__ import annotations

# Standard library imports
import logging.config
from importlib.resources import files
from logging import Logger, getLogger
from pathlib import Path
from typing import ClassVar, Dict, Optional

# Third-party imports
import yaml
from pydantic import JsonValue

# First-party imports
from swarm_logging.models.enums import LogFormat
from swarm_logging.models.exceptions import (
    SELoggingConfigurationRefusedError,
    SELoggingConfigurationUnreadableError,
)
from swarm_logging.models.logging_config import LoggingConfig


class LoggingConfigurator:
    """Configure the standard logging of a process from a ``dictConfig`` file.

    Attributes:
        REFERENCE_PATH (Path): The reference configuration shipped with the package.
        JSON_FORMATTER (str): The dotted path of the JSON formatter.
        JSON_FORMATTER_ENTRY (Dict[str, str]): The ``dictConfig`` entry of a formatter built by the JSON formatter.
        ENCODING (str): The encoding of the configuration file.
        FORMATTERS_KEY (str): The ``dictConfig`` key of the formatters.
        HANDLERS_KEY (str): The ``dictConfig`` key of the handlers.
        FILENAME_KEY (str): The key of a file handler's path.
        config (LoggingConfig): Where the configuration file is and how records are written.
        logger (Logger): Logger instance.

    Notes:
        - In JSON mode every formatter becomes the JSON one, so that a copied file with its own formatters still
          writes one JSON document per line in production.
        - The folder of each file handler is created, because a rotating file handler fails when its folder is missing.
    """

    REFERENCE_PATH: ClassVar[Path] = Path(str(files("swarm_logging").joinpath("conf", "logger.yaml")))
    JSON_FORMATTER: ClassVar[str] = "swarm_logging.formatters.json_formatter.JsonFormatter"
    JSON_FORMATTER_ENTRY: ClassVar[Dict[str, str]] = {"()": JSON_FORMATTER}
    ENCODING: ClassVar[str] = "utf-8"
    FORMATTERS_KEY: ClassVar[str] = "formatters"
    HANDLERS_KEY: ClassVar[str] = "handlers"
    FILENAME_KEY: ClassVar[str] = "filename"

    def __init__(self, config: LoggingConfig, logger: Optional[Logger] = None) -> None:
        """Initialise the configurator.

        Args:
            config (LoggingConfig): Where the configuration file is and how records are written.
            logger (Optional[Logger]): Logger instance.
        """
        self.config = config
        self.logger = logger if logger else getLogger(__name__)

    ############################
    # Internal Helpers Methods #
    ############################

    def _read(self, path: Path) -> Dict[str, JsonValue]:
        """Read the configuration file.

        Args:
            path (Path): The YAML file.

        Returns:
            Dict[str, JsonValue]: The configuration.

        Raises:
            SELoggingConfigurationUnreadableError: If the file cannot be read or is not a mapping.
        """
        try:
            with path.open(encoding=self.ENCODING) as stream:
                content = yaml.safe_load(stream)
        except (OSError, yaml.YAMLError) as error:
            self.logger.error("Cannot read the logging configuration: %s.", type(error).__name__)
            raise SELoggingConfigurationUnreadableError(
                f"Cannot read the logging configuration {str(path)!r}."
            ) from error
        if not isinstance(content, dict):
            self.logger.error("The logging configuration is not a mapping.")
            raise SELoggingConfigurationUnreadableError(
                f"Invalid logging configuration {str(path)!r}. Must be a mapping."
            )
        return content

    def _apply_format(self, content: Dict[str, JsonValue]) -> None:
        """Replace the formatters with the JSON one when the format is JSON.

        Args:
            content (Dict[str, JsonValue]): The configuration, changed in place.
        """
        match self.config.format:
            case LogFormat.JSON:
                formatters = content.get(self.FORMATTERS_KEY)
                if isinstance(formatters, dict):
                    for name in list(formatters):
                        formatters[name] = dict(self.JSON_FORMATTER_ENTRY)
                    self.logger.debug("Replaced %d formatters with the JSON one.", len(formatters))
                else:
                    self.logger.debug("The logging configuration has no formatters to replace.")
            case LogFormat.COLOURED:
                self.logger.debug("Kept the formatters of the file.")

    def _create_folders(self, content: Dict[str, JsonValue]) -> None:
        """Create the parent folder of each handler file.

        Args:
            content (Dict[str, JsonValue]): The configuration.
        """
        handlers = content.get(self.HANDLERS_KEY)
        if not isinstance(handlers, dict):
            self.logger.debug("The logging configuration has no handlers: no folder to create.")
            return
        for name, handler in handlers.items():
            if not isinstance(handler, dict):
                self.logger.debug("Skipped the handler %s, which is not a mapping.", name)
                continue
            filename = handler.get(self.FILENAME_KEY)
            if isinstance(filename, str):
                Path(filename).parent.mkdir(parents=True, exist_ok=True)
                self.logger.debug("Ensured the folder of %s exists.", filename)
            else:
                self.logger.debug("The handler %s writes to no file: no folder to create.", name)

    ############################
    # Publicly Exposed Methods #
    ############################

    def configure(self) -> None:
        """Configure logging.

        Raises:
            SELoggingConfigurationUnreadableError: If the file cannot be read.
            SELoggingConfigurationRefusedError: If ``dictConfig`` refuses the configuration.
        """
        if self.config.path:
            path = Path(self.config.path)
            self.logger.debug("Using the logging configuration %s.", path)
        else:
            path = self.REFERENCE_PATH
            self.logger.debug("Using the reference logging configuration.")
        self.logger.debug("Reading the logging configuration from %s.", path)
        content = self._read(path)
        self._apply_format(content)
        self._create_folders(content)
        try:
            logging.config.dictConfig(content)
        except (ValueError, TypeError, AttributeError, ImportError) as error:
            self.logger.error("The logging configuration was refused: %s.", type(error).__name__)
            raise SELoggingConfigurationRefusedError(f"The logging configuration {str(path)!r} was refused.") from error
        self.logger.info("Configured logging from %s in %s format.", path, self.config.format.value)
