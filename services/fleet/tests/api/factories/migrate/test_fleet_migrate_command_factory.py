from __future__ import annotations

from fleet.api.cli.commands.migrate_command import MigrateCommand
from fleet.api.factories.migrate.migrate_command_factory import MigrateCommandFactory
from fleet.models.config.fleet_config import FleetConfig
from swarm_lifecycle.factories.async_runnable_factory import AsyncRunnableFactory


class TestFleetMigrateCommandFactory:
    def test_create_returns_a_migrate_command_with_the_postgres_status_interval(self) -> None:
        config = FleetConfig()

        command = MigrateCommandFactory(config).create()

        assert isinstance(command, MigrateCommand)
        assert command.status_interval_s == config.postgres.status_interval_s

    def test_the_factory_is_an_async_runnable_factory(self) -> None:
        assert isinstance(MigrateCommandFactory(FleetConfig()), AsyncRunnableFactory)

    def test_create_returns_a_new_command_on_each_call(self) -> None:
        factory = MigrateCommandFactory(FleetConfig())

        assert factory.create() is not factory.create()
