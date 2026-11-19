from __future__ import annotations


class SEAsyncRunnableInvalidStatusIntervalError(ValueError):
    """Raised when an async runnable is given a status interval that is not a positive number of seconds."""
