from __future__ import annotations

# First-party imports
from swarm_models.models.events.exceptions.actor.se_invalid_actor_exception import SEInvalidActorException


class SEActorInvalidAgentName(SEInvalidActorException):
    """Exception raised when an invalid ``agent_name`` is provided."""
