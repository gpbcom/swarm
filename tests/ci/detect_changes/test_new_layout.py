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
    write_repo,
)


class TestNewLayout:
    NEW_FILES: ClassVar[Dict[str, str]] = {
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
    EVERY_SERVICE = '["alpha","beta","delta","gamma"]'

    def repo(self, root: Path) -> None:
        write_repo(root)
        for relative, content in self.NEW_FILES.items():
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")

    @pytest.mark.parametrize(
        ("path", "apps"),
        [
            ("backend/swarm-service/src/swarm_service/drones/x.py", '["gamma"]'),
            ("backend/swarm-api/src/swarm_api/missions/x.py", '["delta","gamma"]'),
            ("backend/swarm-storage/tests/drones/test_x.py", '["gamma"]'),
            ("backend/swarm-models/src/swarm_models/unowned/x.py", "[]"),
            ("backend/apps/delta/src/beta/main.py", '["delta"]'),
        ],
    )
    def test_a_domain_change_selects_the_apps_that_own_it(self, tmp_path: Path, path: str, apps: str) -> None:
        self.repo(tmp_path)
        assert outputs(run_detector(tmp_path, [path]))[SERVICES_KEY] == apps

    def test_a_layer_change_also_selects_the_old_services_that_depend_on_it(self, tmp_path: Path) -> None:
        self.repo(tmp_path)
        (tmp_path / "services" / "alpha" / "pyproject.toml").write_text(
            "[project]\nname = 'alpha'\ndependencies = ['swarm-models>=0.1']\n", encoding="utf-8"
        )
        values = outputs(run_detector(tmp_path, ["backend/swarm-models/src/swarm_models/unowned/x.py"]))
        assert values[SERVICES_KEY] == '["alpha"]'
        assert "services/alpha" in values[IMAGES_KEY]

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
        assert values[SERVICES_KEY] == self.EVERY_SERVICE
        assert values[RUST_KEY] == "true"

    def test_the_new_rust_workspace_behaves_like_the_old_one(self, tmp_path: Path) -> None:
        self.repo(tmp_path)
        (tmp_path / "packages" / "rust" / "Cargo.toml").write_text("[workspace]\nmembers = []\n", encoding="utf-8")
        assert outputs(run_detector(tmp_path, ["rust/core/src/lib.rs"]))[RUST_KEY] == "true"

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
    def test_front_end_packages_and_e2e_behave_like_the_old_shared_folders(self, tmp_path: Path, path: str) -> None:
        self.repo(tmp_path)
        values = outputs(run_detector(tmp_path, [path]))
        assert "frontend/apps/cockpit" in values[TYPESCRIPT_KEY]
        assert "backend/apps/gamma" in values[IMAGES_KEY]

    def test_infra_selects_nothing_like_deploy(self, tmp_path: Path) -> None:
        self.repo(tmp_path)
        values = outputs(run_detector(tmp_path, ["infra/terraform/main.tf"]))
        assert values[SERVICES_KEY] == "[]"
        assert values[IMAGES_KEY] == "[]"
