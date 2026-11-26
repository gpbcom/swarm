from __future__ import annotations

# First-party imports
from swarm_models.simulation.commands.exceptions.command_reply.s_e_invalid_command_reply_exception import (
    SEInvalidCommandReplyException,
)


class SECommandReplyInvalidReason(SEInvalidCommandReplyException):
    """Exception raised when an invalid ``reason`` is provided."""
