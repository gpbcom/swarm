from __future__ import annotations

# First-party imports
from swarm_models.accounts.exceptions.errors.se_nats_accounts_error import SENatsAccountsError


class SENatsJwtInvalidError(SENatsAccountsError):
    """Raised when a NATS JWT cannot be encoded, decoded or verified."""
