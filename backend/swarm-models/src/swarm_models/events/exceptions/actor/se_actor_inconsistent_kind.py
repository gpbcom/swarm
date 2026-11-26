from __future__ import annotations

# First-party imports
from swarm_models.models.events.exceptions.actor.se_invalid_actor_exception import SEInvalidActorException


class SEActorInconsistentKind(SEInvalidActorException):
    """Exception raised when the identifiers of an Actor do not fit its ``kind``."""
