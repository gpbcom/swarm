from __future__ import annotations

# Standard library imports
import os
import subprocess
import sys
from importlib.metadata import entry_points
from pathlib import Path
from typing import ClassVar, Dict

# Third-party imports
import asyncpg

# First-party imports
from swarm_models.config.app_config import AppConfig
from swarm_models.config.gateway.gateway_config import GatewayConfig
from swarm_models.enums import AppName
from swarm_scripts.swarm_apps import SwarmApps


class TestMigrationsScripts:
    SCRIPT: ClassVar[str] = "swarm-migrations-migrate"
    TARGET: ClassVar[str] = "swarm_scripts.migrations.migrate:main"
    OUTBOX_QUERY: ClassVar[str] = "SELECT to_regclass('gateway.outbox') IS NOT NULL"
    UNKNOWN_APP: ClassVar[str] = "nowhere"
    ENCODING: ClassVar[str] = "utf-8"
    TIMEOUT_S: ClassVar[int] = 120

    def run_script(self, cwd: Path, entries: Dict[str, str]) -> subprocess.CompletedProcess[str]:
        environment = {
            name: value
            for name, value in os.environ.items()
            if name not in (SwarmApps.APP_KEY, AppConfig.APP_ROOT_KEY, GatewayConfig.DSN_KEY)
        }
        environment.update(entries)
        return subprocess.run(
            [str(Path(sys.executable).parent / self.SCRIPT)],
            check=False,
            cwd=cwd,
            env=environment,
            capture_output=True,
            text=True,
            encoding=self.ENCODING,
            timeout=self.TIMEOUT_S,
        )

    def test_the_console_script_points_to_its_main(self) -> None:
        assert entry_points(group="console_scripts")[self.SCRIPT].value == self.TARGET

    def test_an_unknown_app_stops_the_migration_with_two(self, tmp_path: Path) -> None:
        result = self.run_script(tmp_path, {SwarmApps.APP_KEY: self.UNKNOWN_APP})

        assert result.returncode == 2, result.stderr

    def test_without_a_dsn_the_migration_of_the_app_fails_with_one(self, tmp_path: Path) -> None:
        result = self.run_script(tmp_path, {SwarmApps.APP_KEY: AppName.GATEWAY.value})

        assert result.returncode == 1, result.stderr
        assert AppName.GATEWAY.value in result.stderr

    async def test_the_migration_of_the_app_creates_its_outbox(self, tmp_path: Path, postgres_dsn: str) -> None:
        result = self.run_script(
            tmp_path, {SwarmApps.APP_KEY: AppName.GATEWAY.value, GatewayConfig.DSN_KEY: postgres_dsn}
        )

        assert result.returncode == 0, result.stderr
        connection = await asyncpg.connect(postgres_dsn)
        try:
            assert await connection.fetchval(self.OUTBOX_QUERY) is True
        finally:
            await connection.close()
