from __future__ import annotations

# First-party imports
from simulator.models.credentials.exceptions.s_e_simulated_credentials_error import SESimulatedCredentialsError


class SESimulatedCredentialsNotSimulatedError(SESimulatedCredentialsError):
    """Raised when a credential is not tagged as simulated."""
