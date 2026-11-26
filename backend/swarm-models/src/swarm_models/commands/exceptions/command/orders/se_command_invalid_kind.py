from __future__ import annotations

# First-party imports
from swarm_models.models.commands.exceptions.command.se_invalid_command_exception import SEInvalidCommandException


class SECommandInvalidKind(SEInvalidCommandException):
    """Exception raised when an invalid ``kind`` is provided."""
