from __future__ import annotations

# Standard library imports
from abc import ABC

# First-party imports
from gateway.api.cli.commands.command import Command
from swarm_lifecycle.factories.runnable_factory import RunnableFactory


class CommandFactory(RunnableFactory[Command], ABC):
    """Abstract factory of the commands of the command line.

    Notes:
        - Concrete factories live in the sub-folders of this package, one per command.
        - Commands are only created by a factory, never by calling their constructor elsewhere in ``src/``.
    """
