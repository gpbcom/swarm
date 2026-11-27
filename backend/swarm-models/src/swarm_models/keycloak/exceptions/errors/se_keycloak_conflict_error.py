from __future__ import annotations

# First-party imports
from swarm_models.keycloak.exceptions.errors.se_keycloak_error import SEKeycloakError


class SEKeycloakConflictError(SEKeycloakError):
    """Raised when the identity provider answers 409, for example when an e-mail is already used."""
