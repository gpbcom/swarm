"""The base exception of the Command model."""

from __future__ import annotations


class SEInvalidCommandException(Exception):
    """Exception raised when an invalid Command is provided."""
