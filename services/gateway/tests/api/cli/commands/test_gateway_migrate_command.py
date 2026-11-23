from __future__ import annotations

# Standard library imports
import subprocess
from typing import ClassVar, List

# Third-party imports
import pytest

# First-party imports
from gateway.api.factories.migrate.migrate_command_factory import MigrateCommandFactory
from gateway.models.config.gateway_config import GatewayConfig
from swarm_lifecycle.models.enums import RunnableStatus


class TestGatewayMigrateCommand:
    PSQL: ClassVar[str] = "psql"
    PSQL_FLAGS: ClassVar[List[str]] = ["-X", "-q", "-At", "-v", "ON_ERROR_STOP=1", "-c"]
    OUTBOX_QUERY: ClassVar[str] = "SELECT to_regclass('gateway.outbox') IS NOT NULL"
    TRUE_OUTPUT: ClassVar[str] = "t"
    ENCODING: ClassVar[str] = "utf-8"

    def outbox_exists(self, dsn: str) -> bool:
        result = subprocess.run(
            [self.PSQL, dsn, *self.PSQL_FLAGS, self.OUTBOX_QUERY],
            capture_output=True,
            text=True,
            encoding=self.ENCODING,
            check=True,
        )
        return result.stdout.strip() == self.TRUE_OUTPUT

    async def test_the_command_creates_the_outbox_and_exits_with_zero(
        self, monkeypatch: pytest.MonkeyPatch, postgres_dsn: str
    ) -> None:
        monkeypatch.setenv(GatewayConfig.DSN_KEY, postgres_dsn)
        command = MigrateCommandFactory(GatewayConfig()).create()

        statuses = [status async for status in command.execute()]

        assert statuses[-1] == RunnableStatus.EXECUTED
        assert command.exit_code == 0
        assert self.outbox_exists(postgres_dsn)

    async def test_without_a_dsn_the_command_exits_with_one_and_raises_nothing(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv(GatewayConfig.DSN_KEY, raising=False)
        command = MigrateCommandFactory(GatewayConfig()).create()

        statuses = [status async for status in command.execute()]

        assert RunnableStatus.EXECUTED not in statuses
        assert command.exit_code == 1
