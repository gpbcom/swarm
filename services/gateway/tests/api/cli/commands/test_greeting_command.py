from __future__ import annotations

# Third-party imports
import pytest

# First-party imports
from gateway.api.cli.commands.command import Command
from gateway.api.cli.commands.greeting_command import GreetingCommand
from swarm_lifecycle.runnables.runnable import Runnable


class TestGreetingCommand:
    def test_execute_prints_the_greeting_and_leaves_the_exit_code_at_zero(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        command = GreetingCommand()

        command.execute()

        assert capsys.readouterr().out == "Hello from swarm!\n"
        assert command.exit_code == 0

    def test_it_is_a_command_and_a_runnable(self) -> None:
        command = GreetingCommand()

        assert isinstance(command, Command)
        assert isinstance(command, Runnable)

    def test_a_command_cannot_be_instantiated(self) -> None:
        with pytest.raises(TypeError):
            Command()  # type: ignore[abstract]
