from __future__ import annotations

# First-party imports
from simulator.models.commands.exceptions.mavlink_command_spec.s_e_invalid_mavlink_command_spec_exception import (
    SEInvalidMavlinkCommandSpecException,
)


class SEMavlinkCommandSpecInvalidCommandId(SEInvalidMavlinkCommandSpecException):
    """Exception raised when an invalid ``command_id`` is provided."""
