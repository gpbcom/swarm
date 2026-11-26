from __future__ import annotations

# First-party imports
from swarm_models.commands.exceptions.command.se_invalid_command_exception import SEInvalidCommandException


class SECommandInvalidMissionId(SEInvalidCommandException):
    """Exception raised when an invalid ``mission_id`` is provided."""
