from __future__ import annotations

# First-party imports
from simulator.models.commands.exceptions.command_reply.s_e_invalid_command_reply_exception import (
    SEInvalidCommandReplyException,
)


class SECommandReplyRefusedWithoutReason(SEInvalidCommandReplyException):
    """Exception raised when a refused reply carries no ``reason``."""
