from __future__ import annotations

# Standard library imports
from argparse import ArgumentParser
from logging import Logger, getLogger
from pathlib import Path
from typing import ClassVar, Optional


class CliOptions:
    """The options of the ``swarm-flight-engine`` command line, and the files it reads by default.

    Attributes:
        CONFIG_FLAG (ClassVar[str]): The option that names the configuration file.
        DEFAULT_CONFIG (ClassVar[str]): The configuration file when the option is left out.
        LOGGER_FILE (ClassVar[str]): The logging configuration file.
        logger (Logger): Logger instance.
    """

    CONFIG_FLAG: ClassVar[str] = "--config"
    DEFAULT_CONFIG: ClassVar[str] = "conf/app.yaml"
    LOGGER_FILE: ClassVar[str] = "conf/logger.yaml"

    def __init__(self, logger: Optional[Logger] = None) -> None:
        """Initialise the options reader.

        Args:
            logger (Optional[Logger]): Logger instance.
        """
        self.logger = logger if logger else getLogger(__name__)

    ############################
    # Publicly Exposed Methods #
    ############################

    def config_path(self) -> Path:
        """Read the configuration file from the command line.

        Returns:
            Path: The file given with ``--config``, or ``conf/app.yaml``.
        """
        parser = ArgumentParser()
        parser.add_argument(self.CONFIG_FLAG, type=Path, default=Path(self.DEFAULT_CONFIG))
        path: Path = parser.parse_args().config
        self.logger.debug("The configuration file is %s.", path)
        return path
