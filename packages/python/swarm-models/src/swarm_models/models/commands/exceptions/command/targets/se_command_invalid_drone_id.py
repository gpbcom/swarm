"""Exception raised when an invalid ``drone_id`` is provided."""

from __future__ import annotations

from swarm_models.models.commands.exceptions.command.se_invalid_command_exception import SEInvalidCommandException


class SECommandInvalidDroneId(SEInvalidCommandException):
    """Exception raised when an invalid ``drone_id`` is provided."""
