from __future__ import annotations

from swarm_models.models.events.exceptions.actor.se_invalid_actor_exception import SEInvalidActorException


class SEActorInvalidKind(SEInvalidActorException):
    """Exception raised when an invalid ``kind`` is provided."""
