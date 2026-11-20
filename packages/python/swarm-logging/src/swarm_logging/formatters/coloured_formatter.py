from __future__ import annotations

# Standard library imports
import logging
from typing import ClassVar, Dict


class ColouredFormatter(logging.Formatter):
    """Format a log record as one line wrapped in the colour of its level.

    Attributes:
        COLOURS (Dict[int, str]): The ANSI colour code of each standard level.
        RESET (str): The ANSI code that ends a colour.

    Notes:
        - The log file holds the colour codes too, so read it with ``tail -f`` or ``less -R``.
        - A level with no colour, such as a custom level, gives the plain line.
    """

    COLOURS: ClassVar[Dict[int, str]] = {
        logging.DEBUG: "\x1b[36m",
        logging.INFO: "\x1b[32m",
        logging.WARNING: "\x1b[33m",
        logging.ERROR: "\x1b[31m",
        logging.CRITICAL: "\x1b[1;31m",
    }
    RESET: ClassVar[str] = "\x1b[0m"

    ############################
    # Publicly Exposed Methods #
    ############################

    def format(self, record: logging.LogRecord) -> str:
        """Format one record in the colour of its level.

        Args:
            record (logging.LogRecord): The record to format.

        Returns:
            str: The formatted line, with the colour code and the reset around it when the level has a colour.
        """
        line = super().format(record)
        colour = self.COLOURS.get(record.levelno)
        if colour is None:
            return line
        return f"{colour}{line}{self.RESET}"
