from __future__ import annotations

# First-party imports
from gateway.api.cli.commands.command import Command


class GreetingCommand(Command):
    """Command that prints the greeting of the gateway.

    Attributes:
        exit_code (int): Exit code of the command, always 0.
        logger (Logger): Logger instance.

    Notes:
        Only ``api/cli/`` prints, because this output is for the person at the terminal.
    """

    ############################
    # Publicly Exposed Methods #
    ############################

    def initialize(self) -> None:
        """Prepare the command, which needs nothing."""
        self.logger.debug("Nothing to acquire for the greeting.")

    def run(self) -> None:
        """Print the greeting."""
        print("Hello from swarm!")
        self.logger.info("Printed the greeting.")

    def close(self) -> None:
        """Release nothing, because nothing was acquired."""
        self.logger.debug("Nothing to release for the greeting.")
