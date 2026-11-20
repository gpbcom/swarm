from __future__ import annotations

# First-party imports
from swarm_models.models.commands.exceptions.command.se_invalid_command_exception import SEInvalidCommandException


class SECommandWrongLane(SEInvalidCommandException):
    """Exception raised when a safety kind is sent on the normal lane."""
