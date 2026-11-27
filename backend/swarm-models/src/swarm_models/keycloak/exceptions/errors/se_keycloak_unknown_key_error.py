from __future__ import annotations

# First-party imports
from swarm_models.keycloak.exceptions.errors.se_keycloak_error import SEKeycloakError


class SEKeycloakUnknownKeyError(SEKeycloakError):
    """Raised when the identity provider publishes no key for the token's key identifier."""
