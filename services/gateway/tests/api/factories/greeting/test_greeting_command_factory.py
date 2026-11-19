from __future__ import annotations

import pytest

from gateway.api.cli.commands.greeting_command import GreetingCommand
from gateway.api.factories.command_factory import CommandFactory
from gateway.api.factories.greeting.greeting_command_factory import GreetingCommandFactory
from swarm_lifecycle.factories.runnable_factory import RunnableFactory


class TestGreetingCommandFactory:
    def test_create_returns_a_greeting_command(self) -> None:
        assert isinstance(GreetingCommandFactory().create(), GreetingCommand)

    def test_create_returns_a_new_command_on_each_call(self) -> None:
        factory = GreetingCommandFactory()

        assert factory.create() is not factory.create()

    def test_the_factory_is_a_command_factory_and_a_runnable_factory(self) -> None:
        factory = GreetingCommandFactory()

        assert isinstance(factory, CommandFactory)
        assert isinstance(factory, RunnableFactory)

    def test_a_command_factory_cannot_be_instantiated(self) -> None:
        with pytest.raises(TypeError):
            CommandFactory()  # type: ignore[abstract]
