from __future__ import annotations

# First-party imports
from swarm_models.simulation.commands.exceptions.mavlink_command_spec.s_e_invalid_mavlink_command_spec_exception import (
    SEInvalidMavlinkCommandSpecException,
)


class SEMavlinkCommandSpecInvalidParam1(SEInvalidMavlinkCommandSpecException):
    """Exception raised when an invalid ``param1`` is provided."""
