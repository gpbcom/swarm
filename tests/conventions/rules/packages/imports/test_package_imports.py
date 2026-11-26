from __future__ import annotations

# Standard library imports
from pathlib import Path
from typing import ClassVar, Dict, List

# Third-party imports
import pytest

# First-party imports
from tests.conventions.helpers import write_files
from tests.conventions.rules.packages.imports.package_imports import PackageImports


class TestPackageImports:
    BASE: ClassVar[Dict[str, str]] = {
        "backend/libs/swarm-lifecycle/src/swarm_lifecycle/a.py": "",
        "backend/libs/swarm-logging/src/swarm_logging/a.py": "",
        "backend/libs/swarm-catalog/src/swarm_catalog/a.py": "",
        "backend/libs/swarm-web/src/swarm_web/a.py": "",
        "backend/swarm-models/src/swarm_models/a.py": "",
        "backend/swarm-storage/src/swarm_storage/a.py": "",
        "backend/swarm-clients/src/swarm_clients/a.py": "",
        "backend/swarm-service/src/swarm_service/a.py": "",
        "backend/swarm-api/src/swarm_api/a.py": "",
        "backend/apps/gateway/src/swarm_gateway/main.py": "",
        "scripts/export.py": "",
    }

    def violations_of(self, tmp_path: Path, path: str, source: str) -> List[str]:
        write_files(tmp_path, self.BASE)
        write_files(tmp_path, {path: source})
        return PackageImports().violations(tmp_path)

    def test_the_rule_has_its_name(self) -> None:
        assert PackageImports.NAME == "package_imports"

    @pytest.mark.parametrize(
        ("path", "source"),
        [
            ("backend/libs/swarm-web/src/swarm_web/a.py", "from swarm_lifecycle.x import Y\nimport yaml\n"),
            (
                "backend/swarm-models/src/swarm_models/a.py",
                "from swarm_catalog.m import Y\nfrom swarm_models.b import Z\n",
            ),
            (
                "backend/swarm-storage/src/swarm_storage/a.py",
                "from swarm_models.m import Y\nfrom swarm_logging.m import Z\n",
            ),
            (
                "backend/swarm-clients/src/swarm_clients/a.py",
                "from swarm_nats.m import Y\nfrom swarm_models import m\n",
            ),
            (
                "backend/swarm-service/src/swarm_service/a.py",
                "from swarm_storage.m import Y\nfrom swarm_clients.m import Z\n",
            ),
            ("backend/swarm-api/src/swarm_api/a.py", "from swarm_service.m import Y\nfrom swarm_web.m import Z\n"),
            ("backend/apps/gateway/src/swarm_gateway/main.py", "from swarm_models.config.gateway.c import C\n"),
            ("backend/apps/gateway/src/swarm_gateway/main.py", "from swarm_models.config import gateway\n"),
            (
                "scripts/export.py",
                "from swarm_api.m import Y\nfrom swarm_models.m import Z\nfrom swarm_web.m import W\n",
            ),
        ],
    )
    def test_allowed_imports_are_accepted(self, tmp_path: Path, path: str, source: str) -> None:
        assert self.violations_of(tmp_path, path, source) == []

    @pytest.mark.parametrize(
        ("path", "source"),
        [
            ("backend/libs/swarm-web/src/swarm_web/a.py", "from swarm_models.x import Y\n"),
            ("backend/swarm-models/src/swarm_models/a.py", "from swarm_logging.x import Y\n"),
            ("backend/swarm-models/src/swarm_models/a.py", "from swarm_service.x import Y\n"),
            ("backend/swarm-storage/src/swarm_storage/a.py", "from swarm_clients.x import Y\n"),
            ("backend/swarm-clients/src/swarm_clients/a.py", "from swarm_storage.x import Y\n"),
            ("backend/swarm-service/src/swarm_service/a.py", "from swarm_api.x import Y\n"),
            ("backend/swarm-api/src/swarm_api/a.py", "from swarm_storage.x import Y\n"),
            ("backend/swarm-api/src/swarm_api/a.py", "from swarm_clients.x import Y\n"),
            ("backend/apps/gateway/src/swarm_gateway/main.py", "from swarm_storage.x import Y\n"),
            ("backend/apps/gateway/src/swarm_gateway/main.py", "from swarm_models.config.fleet.c import C\n"),
            ("backend/apps/gateway/src/swarm_gateway/main.py", "from swarm_models.shared.c import C\n"),
            ("scripts/export.py", "from swarm_storage.x import Y\n"),
        ],
    )
    def test_refused_imports_are_reported(self, tmp_path: Path, path: str, source: str) -> None:
        found = self.violations_of(tmp_path, path, source)
        assert len(found) == 1
        assert path in found[0]
        assert ":1:" in found[0]

    def test_a_third_party_import_is_never_refused(self, tmp_path: Path) -> None:
        source = "import yaml\nfrom fastapi import FastAPI\n"
        assert self.violations_of(tmp_path, "backend/swarm-models/src/swarm_models/a.py", source) == []

    def test_a_root_without_backend_has_no_violation(self, tmp_path: Path) -> None:
        assert PackageImports().violations(tmp_path) == []
