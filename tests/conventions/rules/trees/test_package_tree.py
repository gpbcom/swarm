from __future__ import annotations

# Standard library imports
from pathlib import Path
from typing import ClassVar, Dict

# First-party imports
from tests.conventions.helpers import write_files
from tests.conventions.rules.trees.package_tree import PackageTree


class TestPackageTree:
    LAYOUT: ClassVar[Dict[str, str]] = {
        "backend/libs/swarm-web/src/swarm_web/a.py": "",
        "backend/libs/swarm-catalog/src/swarm_catalog/a.py": "",
        "backend/swarm-models/src/swarm_models/a.py": "",
        "backend/swarm-service/src/swarm_service/a.py": "",
        "backend/swarm-service/src/swarm_service/__pycache__/b.py": "",
        "backend/swarm-other/src/swarm_other/a.py": "",
        "backend/apps/flight-engine/src/swarm_flight_engine/main.py": "",
        "backend/apps/flight-engine/pyproject.toml": '[tool.swarm]\ndomains = ["flight", "fleet"]\n',
        "backend/apps/gateway/src/swarm_gateway/main.py": "",
        "scripts/openapi/export.py": "",
    }

    def test_discovery_finds_kernel_layers_apps_and_scripts_in_order(self, tmp_path: Path) -> None:
        write_files(tmp_path, self.LAYOUT)
        found = [(tree.role, tree.module) for tree in PackageTree.discover(tmp_path)]
        assert found == [
            (PackageTree.KERNEL, "swarm_catalog"),
            (PackageTree.KERNEL, "swarm_web"),
            ("models", "swarm_models"),
            ("service", "swarm_service"),
            (PackageTree.APP, "swarm_flight_engine"),
            (PackageTree.APP, "swarm_gateway"),
            (PackageTree.SCRIPTS, "scripts"),
        ]

    def test_discovery_of_a_root_without_backend_is_empty(self, tmp_path: Path) -> None:
        assert PackageTree.discover(tmp_path) == []

    def test_python_files_skip_the_cache_and_are_sorted(self, tmp_path: Path) -> None:
        write_files(tmp_path, self.LAYOUT)
        service = next(tree for tree in PackageTree.discover(tmp_path) if tree.module == "swarm_service")
        assert [service.relative(path) for path in service.python_files()] == [
            "backend/swarm-service/src/swarm_service/a.py"
        ]

    def test_the_scripts_are_their_own_source_root(self, tmp_path: Path) -> None:
        write_files(tmp_path, self.LAYOUT)
        scripts = PackageTree.discover(tmp_path)[-1]
        assert scripts.source_root == tmp_path / "scripts"
        assert [scripts.relative(path) for path in scripts.python_files()] == ["scripts/openapi/export.py"]

    def test_an_app_reads_its_domains_and_its_config_name(self, tmp_path: Path) -> None:
        write_files(tmp_path, self.LAYOUT)
        app = next(tree for tree in PackageTree.discover(tmp_path) if tree.name == "flight-engine")
        assert app.domains() == ["flight", "fleet"]
        assert app.app_name == "flight_engine"

    def test_an_app_without_a_project_file_has_no_domains(self, tmp_path: Path) -> None:
        write_files(tmp_path, self.LAYOUT)
        app = next(tree for tree in PackageTree.discover(tmp_path) if tree.name == "gateway")
        assert app.domains() == []

    def test_the_layers(self) -> None:
        assert PackageTree.LAYERS == ("models", "storage", "clients", "service", "api")
