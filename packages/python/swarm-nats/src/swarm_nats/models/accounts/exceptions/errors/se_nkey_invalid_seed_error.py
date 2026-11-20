from __future__ import annotations

from swarm_nats.models.accounts.exceptions.errors.se_nats_accounts_error import SENatsAccountsError


class SENkeyInvalidSeedError(SENatsAccountsError):
    """Raised when a seed is not a valid NKey seed."""
