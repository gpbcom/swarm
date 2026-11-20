from __future__ import annotations

# First-party imports
from gateway.api.cli.commands.command import Command
from gateway.api.cli.commands.greeting_command import GreetingCommand
from gateway.api.factories.command_factory import CommandFactory


class GreetingCommandFactory(CommandFactory):
    """Factory of the command that prints the greeting of the gateway."""

    ############################
    # Internal Helpers Methods #
    ############################

    def _build(self) -> Command:
        """Build one greeting command.

        Returns:
            Command: A new ``GreetingCommand``.
        """
        self.logger.debug("Building a greeting command.")
        return GreetingCommand()
