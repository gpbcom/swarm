from __future__ import annotations

# First-party imports
from gateway.api.cli.commands.migrate_command import MigrateCommand
from gateway.api.factories.migrate.migrate_command_factory import MigrateCommandFactory
from gateway.models.config.gateway_config import GatewayConfig
from swarm_lifecycle.factories.async_runnable_factory import AsyncRunnableFactory


class TestGatewayMigrateCommandFactory:
    def test_create_returns_a_migrate_command_with_the_configured_status_interval(self) -> None:
        config = GatewayConfig()

        command = MigrateCommandFactory(config).create()

        assert isinstance(command, MigrateCommand)
        assert command.status_interval_s == config.postgres.status_interval_s

    def test_the_factory_is_an_async_runnable_factory(self) -> None:
        assert isinstance(MigrateCommandFactory(GatewayConfig()), AsyncRunnableFactory)

    def test_create_returns_a_new_command_on_each_call(self) -> None:
        factory = MigrateCommandFactory(GatewayConfig())

        assert factory.create() is not factory.create()
