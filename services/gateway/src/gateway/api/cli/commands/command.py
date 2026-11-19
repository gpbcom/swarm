from __future__ import annotations

# Standard library imports
from logging import Logger
from typing import Optional

# First-party imports
from swarm_lifecycle.runnables.runnable import Runnable


class Command(Runnable):
    """Base class of every command of the command line.

    Attributes:
        exit_code (int): Exit code of the command, read after ``execute()``. It is 0 unless the command sets it.
        logger (Logger): Logger instance.

    Notes:
        Inputs go to the constructor and the result is read from ``exit_code`` afterwards.
    """

    def __init__(self, logger: Optional[Logger] = None) -> None:
        """Initialise the command.

        Args:
            logger (Optional[Logger]): Logger to use. A default logger is used when it is ``None``.
        """
        super().__init__(logger)
        self.exit_code = 0
