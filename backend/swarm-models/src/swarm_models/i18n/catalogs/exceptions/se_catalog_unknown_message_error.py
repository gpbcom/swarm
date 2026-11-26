from __future__ import annotations

# First-party imports
from swarm_i18n.models.catalogs.exceptions.se_catalog_error import SECatalogError


class SECatalogUnknownMessageError(SECatalogError):
    """Raised when a message is not in the catalogue."""
