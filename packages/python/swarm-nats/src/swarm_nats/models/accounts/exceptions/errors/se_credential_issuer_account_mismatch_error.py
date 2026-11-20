from __future__ import annotations

from swarm_nats.models.accounts.exceptions.errors.se_nats_accounts_error import SENatsAccountsError


class SECredentialIssuerAccountMismatchError(SENatsAccountsError):
    """Raised when a credential is requested for an operator that does not own the account."""
