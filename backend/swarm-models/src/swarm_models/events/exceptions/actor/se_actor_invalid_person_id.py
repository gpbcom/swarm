from __future__ import annotations

# First-party imports
from swarm_models.events.exceptions.actor.se_invalid_actor_exception import SEInvalidActorException


class SEActorInvalidPersonId(SEInvalidActorException):
    """Exception raised when an invalid ``person_id`` is provided."""
