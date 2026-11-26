from __future__ import annotations

# First-party imports
from swarm_models.i18n.catalogs.exceptions.se_catalog_error import SECatalogError


class SECatalogUnknownMessageError(SECatalogError):
    """Raised when a message is not in the catalogue."""
