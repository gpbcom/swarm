from __future__ import annotations

# Standard library imports
from logging import Logger, getLogger
from typing import Optional

# First-party imports
from simulator.models.commands.command_reply import CommandReply
from simulator.service.commands.simulated_command_service import SimulatedCommandService
from swarm_models.models.commands.command import Command


class CommandEndpoint:
    """The entry point of the command bus: it hands each command to the service and returns its reply.

    Attributes:
        service (SimulatedCommandService): The service that carries out the commands.
        logger (Logger): Logger instance.

    Notes:
        - It holds no business rule: a refusal is the service's reply, not an error of the endpoint.
    """

    def __init__(self, service: SimulatedCommandService, logger: Optional[Logger] = None) -> None:
        """Create the endpoint.

        Args:
            service (SimulatedCommandService): The service that carries out the commands.
            logger (Optional[Logger]): Logger instance.
        """
        self.service = service
        self.logger = logger if logger else getLogger(__name__)

    ############################
    # Publicly Exposed Methods #
    ############################

    async def handle(self, command: Command) -> CommandReply:
        """Answer one command of the bus.

        Args:
            command (Command): The command received.

        Returns:
            CommandReply: The reply of the service.
        """
        self.logger.debug("Received command %s of kind %s.", command.id, command.kind.value)
        reply = await self.service.handle(command)
        self.logger.info("Answered command %s with %s.", command.id, reply.verdict.value)
        return reply
