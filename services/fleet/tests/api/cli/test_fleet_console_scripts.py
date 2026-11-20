from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import ClassVar, Dict, List

from fleet.api.rest.fleet_rest_app import FleetRestApp
from fleet.models.config.fleet_config import FleetConfig


class TestFleetConsoleScripts:
    ROOT: ClassVar[Path] = Path(__file__).resolve().parents[5]
    OPENAPI_SCRIPT: ClassVar[str] = "swarm-fleet-openapi"
    MIGRATE_SCRIPT: ClassVar[str] = "swarm-fleet-migrate"
    CHECK_FLAG: ClassVar[str] = "--check"
    OUTPUT_FLAG: ClassVar[str] = "--output"
    OUTPUT_NAME: ClassVar[str] = "fleet.json"
    ENCODING: ClassVar[str] = "utf-8"

    def run_script(
        self, name: str, arguments: List[str], environment: Dict[str, str]
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [str(Path(sys.executable).parent / name), *arguments],
            cwd=self.ROOT,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
            timeout=120,
        )

    def test_the_openapi_check_passes_on_the_published_document(self) -> None:
        result = self.run_script(self.OPENAPI_SCRIPT, [self.CHECK_FLAG], dict(os.environ))

        assert result.returncode == 0, result.stderr

    def test_the_openapi_output_writes_the_published_text(self, tmp_path: Path) -> None:
        target = tmp_path / self.OUTPUT_NAME

        result = self.run_script(self.OPENAPI_SCRIPT, [self.OUTPUT_FLAG, str(target)], dict(os.environ))

        published = self.ROOT / FleetRestApp.OPENAPI_OUTPUT
        assert result.returncode == 0, result.stderr
        assert target.read_text(encoding=self.ENCODING) == published.read_text(encoding=self.ENCODING)

    def test_the_migrate_script_returns_zero_with_the_dsn_set(self, postgres_dsn: str) -> None:
        environment = {**os.environ, FleetConfig.DSN_KEY: postgres_dsn}

        result = self.run_script(self.MIGRATE_SCRIPT, [], environment)

        assert result.returncode == 0, result.stderr
