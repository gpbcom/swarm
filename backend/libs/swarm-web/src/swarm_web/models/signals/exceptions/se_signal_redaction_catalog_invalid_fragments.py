from __future__ import annotations

# First-party imports
from swarm_web.models.signals.exceptions.se_invalid_signal_redaction_catalog_exception import (
    SEInvalidSignalRedactionCatalogException,
)


class SESignalRedactionCatalogInvalidFragments(SEInvalidSignalRedactionCatalogException):
    """Exception raised when invalid ``fragments`` are provided."""
