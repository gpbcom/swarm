from __future__ import annotations


class SEMissionsConfigUnreadable(Exception):
    """Exception raised when the configuration file of the missions service cannot be read.

    Notes:
        **It must not subclass ``ValueError``**, because pydantic would wrap it in a validation error.
    """
