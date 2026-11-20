from __future__ import annotations

from logging import Logger, getLogger
from typing import ClassVar, List

import asyncpg
import pytest

from fleet.api.cli.commands.migrate_command import MigrateCommand
from fleet.api.factories.migrate.migrate_command_factory import MigrateCommandFactory
from fleet.models.config.fleet_config import FleetConfig
from swarm_lifecycle.models.enums import RunnableStatus


class TestFleetMigrateCommand:
    LOGGER: ClassVar[Logger] = getLogger(__name__)
    OUTBOX_QUERY: ClassVar[str] = "SELECT to_regclass('fleet.outbox') IS NOT NULL"

    async def test_a_run_ends_executed_and_creates_the_outbox(
        self, monkeypatch: pytest.MonkeyPatch, postgres_dsn: str
    ) -> None:
        monkeypatch.setenv(FleetConfig.DSN_KEY, postgres_dsn)
        command: MigrateCommand = MigrateCommandFactory(FleetConfig()).create()

        statuses: List[RunnableStatus] = [status async for status in command.execute()]

        connection = await asyncpg.connect(postgres_dsn)
        try:
            outbox_exists = await connection.fetchval(self.OUTBOX_QUERY)
        except asyncpg.PostgresError as error:
            self.LOGGER.error("Outbox query failed: %s.", type(error).__name__)
            raise
        finally:
            await connection.close()
        assert statuses[-1] == RunnableStatus.EXECUTED
        assert command.exit_code == 0
        assert outbox_exists is True

    async def test_a_run_without_the_dsn_exits_with_one_and_raises_nothing(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv(FleetConfig.DSN_KEY, raising=False)
        command: MigrateCommand = MigrateCommandFactory(FleetConfig()).create()

        statuses: List[RunnableStatus] = [status async for status in command.execute()]

        assert command.exit_code == 1
        assert statuses[-1] != RunnableStatus.EXECUTED
