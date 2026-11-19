"""Exception raised when an invalid ``lane`` is provided."""

from __future__ import annotations

from swarm_models.models.commands.exceptions.command.se_invalid_command_exception import SEInvalidCommandException


class SECommandInvalidLane(SEInvalidCommandException):
    """Exception raised when an invalid ``lane`` is provided."""
