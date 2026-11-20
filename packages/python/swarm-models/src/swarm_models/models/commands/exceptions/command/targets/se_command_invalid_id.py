from __future__ import annotations

from swarm_models.models.commands.exceptions.command.se_invalid_command_exception import SEInvalidCommandException


class SECommandInvalidId(SEInvalidCommandException):
    """Exception raised when an invalid ``id`` is provided."""
