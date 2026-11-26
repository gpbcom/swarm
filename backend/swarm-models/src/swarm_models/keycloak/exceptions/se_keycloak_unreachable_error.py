from __future__ import annotations

# First-party imports
from swarm_models.keycloak.exceptions.se_keycloak_error import SEKeycloakError


class SEKeycloakUnreachableError(SEKeycloakError):
    """Raised when the identity provider cannot be reached."""
