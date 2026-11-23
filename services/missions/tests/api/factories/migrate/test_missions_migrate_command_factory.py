from __future__ import annotations

# First-party imports
from missions.api.cli.commands.migrate_command import MigrateCommand
from missions.api.factories.migrate.migrate_command_factory import MigrateCommandFactory
from missions.models.config.missions_config import MissionsConfig


class TestMissionsMigrateCommandFactory:
    def test_create_returns_a_migrate_command_with_the_status_interval_of_the_configuration(self) -> None:
        config = MissionsConfig()

        command = MigrateCommandFactory(config).create()

        assert isinstance(command, MigrateCommand)
        assert command.status_interval_s == config.postgres.status_interval_s
