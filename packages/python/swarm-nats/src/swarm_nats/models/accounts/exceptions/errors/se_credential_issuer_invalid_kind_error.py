from __future__ import annotations

# First-party imports
from swarm_nats.models.accounts.exceptions.errors.se_nats_accounts_error import SENatsAccountsError


class SECredentialIssuerInvalidKindError(SENatsAccountsError):
    """Raised when a credential is requested with a kind that an operator credential cannot have."""
