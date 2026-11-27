from __future__ import annotations


class SEInvalidOperatorEntryException(ValueError):
    """Exception raised when an invalid OperatorEntry is provided.

    Notes:
        It is a ``ValueError``, so that FastAPI answers a body of the wrong type with ``422``.
    """
