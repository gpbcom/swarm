from __future__ import annotations

# First-party imports
from swarm_models.commands.exceptions.command.se_invalid_command_exception import SEInvalidCommandException


class SECommandInvalidDroneId(SEInvalidCommandException):
    """Exception raised when an invalid ``drone_id`` is provided."""
