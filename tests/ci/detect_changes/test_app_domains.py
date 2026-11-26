from __future__ import annotations

# Standard library imports
from pathlib import Path
from typing import ClassVar, Dict

# Third-party imports
import pytest

# First-party imports
from tests.ci.detect_changes.helpers import (
    IMAGES_KEY,
    REPOSITORY_KEY,
    RUST_KEY,
    SERVICES_KEY,
    TYPESCRIPT_KEY,
    outputs,
    run_detector,
)


class TestAppDomains:
    FILES: ClassVar[Dict[str, str]] = {
        "backend/apps/gamma/pyproject.toml": "[project]\nname = 'a'\n[tool.swarm]\ndomains = ['drones', 'missions']\n",
        "backend/apps/gamma/Dockerfile": "FROM scratch\n",
        "backend/apps/delta/pyproject.toml": "[project]\nname = 'b'\n[tool.swarm]\ndomains = ['missions']\n",
        "backend/apps/delta/Dockerfile": "FROM scratch\n",
        "backend/apps/.hidden/pyproject.toml": "[tool.swarm]\ndomains = ['drones']\n",
        "frontend/apps/cockpit/package.json": "{}\n",
        "frontend/apps/cockpit/Dockerfile": "FROM scratch\n",
        "frontend/packages/ui/package.json": "{}\n",
        "rust/Cargo.toml": '[workspace]\nmembers = ["core"]\n',
    }
    EVERY_APP: ClassVar[str] = '["delta","gamma"]'

    def repo(self, root: Path) -> None:
        for relative, content in self.FILES.items():
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")

    @pytest.mark.parametrize(
        ("path", "apps"),
        [
            ("backend/swarm-service/src/swarm_service/drones/x.py", '["gamma"]'),
            ("backend/swarm-api/src/swarm_api/missions/x.py", '["delta","gamma"]'),
            ("backend/swarm-api/src/swarm_api/v1/drones/drone_router.py", '["gamma"]'),
            ("backend/swarm-api/src/swarm_api/v1/missions/mission_router.py", '["delta","gamma"]'),
            ("backend/swarm-api/src/swarm_api/v1/live/live_router.py", '["delta","gamma"]'),
            ("backend/swarm-api/src/swarm_api/handlers/problem_handlers.py", '["delta","gamma"]'),
            ("backend/apps/gamma/Dockerfile", '["gamma"]'),
            ("backend/swarm-storage/tests/drones/test_x.py", '["gamma"]'),
            ("backend/swarm-models/src/swarm_models/unowned/x.py", "[]"),
            ("backend/apps/delta/src/beta/main.py", '["delta"]'),
        ],
    )
    def test_a_domain_change_selects_the_apps_that_own_it(self, tmp_path: Path, path: str, apps: str) -> None:
        self.repo(tmp_path)
        assert outputs(run_detector(tmp_path, [path]))[SERVICES_KEY] == apps

    def test_a_layer_change_runs_the_repository_checks(self, tmp_path: Path) -> None:
        self.repo(tmp_path)
        assert outputs(run_detector(tmp_path, ["backend/swarm-models/src/swarm_models/x.py"]))[REPOSITORY_KEY] == "true"

    @pytest.mark.parametrize(
        "path",
        ["backend/swarm-service/src/swarm_service/shared/x.py", "backend/swarm-service/pyproject.toml"],
    )
    def test_a_layer_wide_change_selects_every_app(self, tmp_path: Path, path: str) -> None:
        self.repo(tmp_path)
        assert outputs(run_detector(tmp_path, [path]))[SERVICES_KEY] == '["delta","gamma"]'

    @pytest.mark.parametrize("path", ["backend/libs/lifecycle/src/x.py", "scripts/tool.py", "rust/core/src/lib.rs"])
    def test_libs_scripts_and_rust_select_everything(self, tmp_path: Path, path: str) -> None:
        self.repo(tmp_path)
        values = outputs(run_detector(tmp_path, [path]))
        assert values[SERVICES_KEY] == self.EVERY_APP
        assert values[RUST_KEY] == "true"

    def test_a_front_end_app_change_selects_its_typescript_and_image(self, tmp_path: Path) -> None:
        self.repo(tmp_path)
        values = outputs(run_detector(tmp_path, ["frontend/apps/cockpit/src/a.ts"]))
        assert values[TYPESCRIPT_KEY] == '["frontend/apps/cockpit"]'
        assert values[IMAGES_KEY] == '["frontend/apps/cockpit"]'

    def test_a_backend_app_change_selects_its_image(self, tmp_path: Path) -> None:
        self.repo(tmp_path)
        values = outputs(run_detector(tmp_path, ["backend/swarm-service/src/swarm_service/drones/x.py"]))
        assert values[IMAGES_KEY] == '["backend/apps/gamma"]'

    @pytest.mark.parametrize("path", ["frontend/packages/ui/src/a.ts", "qa/e2e/a.ts", "infra/compose/e2e.yaml"])
    def test_front_end_packages_and_e2e_select_every_front_end_and_image(self, tmp_path: Path, path: str) -> None:
        self.repo(tmp_path)
        values = outputs(run_detector(tmp_path, [path]))
        assert "frontend/apps/cockpit" in values[TYPESCRIPT_KEY]
        assert "backend/apps/gamma" in values[IMAGES_KEY]

    def test_infra_selects_nothing(self, tmp_path: Path) -> None:
        self.repo(tmp_path)
        values = outputs(run_detector(tmp_path, ["infra/terraform/main.tf"]))
        assert values[SERVICES_KEY] == "[]"
        assert values[IMAGES_KEY] == "[]"
