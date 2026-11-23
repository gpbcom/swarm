from __future__ import annotations

# Standard library imports
import os
import subprocess
import sys
from pathlib import Path
from typing import ClassVar, Dict, Optional

# Third-party imports
import pytest

# First-party imports
from gateway.api.rest.gateway_rest_app import GatewayRestApp
from gateway.models.config.gateway_config import GatewayConfig


class TestGatewayConsoleScripts:
    OPENAPI_SCRIPT: ClassVar[str] = "swarm-gateway-openapi"
    MIGRATE_SCRIPT: ClassVar[str] = "swarm-gateway-migrate"
    CHECK_FLAG: ClassVar[str] = "--check"
    OUTPUT_FLAG: ClassVar[str] = "--output"
    OUTPUT_FILE: ClassVar[str] = "gateway.json"
    ENCODING: ClassVar[str] = "utf-8"
    ROOT_PARENT_INDEX: ClassVar[int] = 5
    TIMEOUT_S: ClassVar[int] = 120

    @pytest.fixture
    def root(self) -> Path:
        return Path(__file__).resolve().parents[self.ROOT_PARENT_INDEX]

    def run_script(self, name: str, root: Path, *arguments: str, env: Optional[Dict[str, str]] = None) -> int:
        result = subprocess.run(
            [str(Path(sys.executable).parent / name), *arguments],
            check=False,
            cwd=root,
            env=env,
            capture_output=True,
            text=True,
            encoding=self.ENCODING,
            timeout=self.TIMEOUT_S,
        )
        return result.returncode

    def test_the_openapi_check_passes_on_the_published_document(self, root: Path) -> None:
        assert self.run_script(self.OPENAPI_SCRIPT, root, self.CHECK_FLAG) == 0

    def test_the_openapi_output_equals_the_published_document(self, root: Path, tmp_path: Path) -> None:
        output = tmp_path / self.OUTPUT_FILE

        code = self.run_script(self.OPENAPI_SCRIPT, root, self.OUTPUT_FLAG, str(output))

        assert code == 0
        published = root / GatewayRestApp.OPENAPI_OUTPUT
        assert output.read_text(encoding=self.ENCODING) == published.read_text(encoding=self.ENCODING)

    def test_the_migrate_script_exits_with_zero(self, root: Path, postgres_dsn: str) -> None:
        environment = os.environ.copy()
        environment[GatewayConfig.DSN_KEY] = postgres_dsn

        assert self.run_script(self.MIGRATE_SCRIPT, root, env=environment) == 0
