from __future__ import annotations


class SEFleetConfigUnreadable(Exception):
    """Exception raised when the configuration file of the fleet service cannot be read.

    Notes:
        - **It must not subclass ``ValueError``**, because pydantic would wrap it in a validation error.
    """
