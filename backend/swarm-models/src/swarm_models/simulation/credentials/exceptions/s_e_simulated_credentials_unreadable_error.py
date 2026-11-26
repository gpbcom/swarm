from __future__ import annotations

# First-party imports
from simulator.models.credentials.exceptions.s_e_simulated_credentials_error import SESimulatedCredentialsError


class SESimulatedCredentialsUnreadableError(SESimulatedCredentialsError):
    """Raised when a credentials file cannot be read or does not hold a valid JWT."""
