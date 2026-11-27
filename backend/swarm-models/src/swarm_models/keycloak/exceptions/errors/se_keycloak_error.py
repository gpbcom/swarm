from __future__ import annotations

# Standard library imports
from typing import ClassVar

# First-party imports
from swarm_models.enums import AccessRefusal


class SEKeycloakError(Exception):
    """Base class for every error raised while asking the identity provider.

    Attributes:
        REFUSAL (AccessRefusal): The refusal the caller of the gateway sees.
    """

    REFUSAL: ClassVar[AccessRefusal] = AccessRefusal.IDENTITY_UNAVAILABLE
