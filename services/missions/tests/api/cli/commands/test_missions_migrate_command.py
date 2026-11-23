from __future__ import annotations

# Standard library imports
from typing import ClassVar, List

# Third-party imports
import asyncpg
import pytest

# First-party imports
from missions.api.factories.migrate.migrate_command_factory import MigrateCommandFactory
from missions.models.config.missions_config import MissionsConfig
from swarm_lifecycle.models.enums import RunnableStatus


class TestMissionsMigrateCommand:
    OUTBOX_QUERY: ClassVar[str] = "SELECT to_regclass('missions.outbox') IS NOT NULL"

    async def test_a_run_creates_the_outbox_and_exits_with_zero(
        self, monkeypatch: pytest.MonkeyPatch, postgres_dsn: str
    ) -> None:
        monkeypatch.setenv(MissionsConfig.DSN_KEY, postgres_dsn)
        command = MigrateCommandFactory(MissionsConfig()).create()
        statuses: List[RunnableStatus] = []

        async for status in command.execute():
            statuses.append(status)

        assert statuses[-1] == RunnableStatus.EXECUTED
        assert command.exit_code == 0
        connection = await asyncpg.connect(postgres_dsn)
        created = await connection.fetchval(self.OUTBOX_QUERY)
        await connection.close()
        assert created is True

    async def test_without_the_dsn_the_exit_code_is_one_and_nothing_is_raised(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv(MissionsConfig.DSN_KEY, raising=False)
        command = MigrateCommandFactory(MissionsConfig()).create()

        async for _ in command.execute():
            pass

        assert command.exit_code == 1
