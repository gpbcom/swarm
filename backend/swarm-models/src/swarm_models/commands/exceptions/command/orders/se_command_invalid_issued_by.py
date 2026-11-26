from __future__ import annotations

# First-party imports
from swarm_models.commands.exceptions.command.se_invalid_command_exception import SEInvalidCommandException


class SECommandInvalidIssuedBy(SEInvalidCommandException):
    """Exception raised when an invalid ``issued_by`` is provided."""
