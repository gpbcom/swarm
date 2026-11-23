from __future__ import annotations

# First-party imports
from simulator.models.commands.exceptions.command_reply.s_e_invalid_command_reply_exception import (
    SEInvalidCommandReplyException,
)


class SECommandReplyInvalidVerdict(SEInvalidCommandReplyException):
    """Exception raised when an invalid ``verdict`` is provided."""
