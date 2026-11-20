from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import ClassVar, Dict, List, Optional

import pytest

from missions.api.rest.missions_rest_app import MissionsRestApp
from missions.models.config.missions_config import MissionsConfig


class TestMissionsConsoleScripts:
    OPENAPI_SCRIPT: ClassVar[str] = "swarm-missions-openapi"
    MIGRATE_SCRIPT: ClassVar[str] = "swarm-missions-migrate"
    CHECK_FLAG: ClassVar[str] = "--check"
    OUTPUT_FLAG: ClassVar[str] = "--output"
    OUTPUT_NAME: ClassVar[str] = "missions.json"
    REPOSITORY_ROOT_DEPTH: ClassVar[int] = 5
    TIMEOUT_S: ClassVar[int] = 120

    def run_script(self, name: str, arguments: List[str], environment: Optional[Dict[str, str]] = None) -> int:
        root = Path(__file__).resolve().parents[self.REPOSITORY_ROOT_DEPTH]
        script = Path(sys.executable).parent / name
        result = subprocess.run(
            [str(script), *arguments],
            check=False,
            cwd=root,
            env=environment,
            capture_output=True,
            timeout=self.TIMEOUT_S,
        )
        return result.returncode

    def test_the_openapi_script_checks_the_published_document(self) -> None:
        assert self.run_script(self.OPENAPI_SCRIPT, [self.CHECK_FLAG]) == 0

    def test_the_openapi_script_writes_the_published_document(self, tmp_path: Path) -> None:
        root = Path(__file__).resolve().parents[self.REPOSITORY_ROOT_DEPTH]
        output = tmp_path / self.OUTPUT_NAME

        code = self.run_script(self.OPENAPI_SCRIPT, [self.OUTPUT_FLAG, str(output)])

        assert code == 0
        published = root / MissionsRestApp.OPENAPI_OUTPUT
        assert output.read_text(encoding="utf-8") == published.read_text(encoding="utf-8")

    def test_the_migrate_script_succeeds_with_the_dsn_set(
        self, monkeypatch: pytest.MonkeyPatch, postgres_dsn: str
    ) -> None:
        monkeypatch.setenv(MissionsConfig.DSN_KEY, postgres_dsn)

        assert self.run_script(self.MIGRATE_SCRIPT, [], dict(os.environ)) == 0
