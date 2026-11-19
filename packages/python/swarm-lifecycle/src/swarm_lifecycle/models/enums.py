from __future__ import annotations

# Standard library imports
from enum import StrEnum, unique


@unique
class RunnableStatus(StrEnum):
    """What an async runnable is doing, as ``AsyncRunnable.execute`` yields it.

    Attributes:
        NOT_STARTED (str): ``execute`` has not started yet.
        INITIALISING (str): ``initialize`` is working.
        RUNNING (str): ``run`` is working.
        EXECUTED (str): The work succeeded and the runnable is closed. It is the last status yielded.
    """

    NOT_STARTED = "not_started"
    INITIALISING = "initialising"
    RUNNING = "running"
    EXECUTED = "executed"
