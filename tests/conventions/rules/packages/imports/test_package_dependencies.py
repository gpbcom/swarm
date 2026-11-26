from __future__ import annotations

# Standard library imports
from pathlib import Path
from typing import ClassVar, Dict, List

# First-party imports
from tests.conventions.helpers import write_files
from tests.conventions.rules.packages.imports.package_dependencies import PackageDependencies


class TestPackageDependencies:
    BASE: ClassVar[Dict[str, str]] = {
        "backend/swarm-models/src/swarm_models/a.py": "",
        "backend/swarm-models/pyproject.toml": "[project]\ndependencies = []\n",
        "backend/libs/swarm-lifecycle/src/swarm_lifecycle/a.py": "",
        "backend/swarm-storage/src/swarm_storage/a.py": "from swarm_models.m import Y\nimport asyncpg\n",
    }

    def violations_of(self, tmp_path: Path, project: str) -> List[str]:
        write_files(tmp_path, self.BASE)
        write_files(tmp_path, {"backend/swarm-storage/pyproject.toml": project})
        return PackageDependencies().violations(tmp_path)

    def test_the_rule_has_its_name(self) -> None:
        assert PackageDependencies.NAME == "package_dependencies"

    def test_exactly_the_needed_dependencies_are_accepted(self, tmp_path: Path) -> None:
        project = '[project]\nname = "swarm-storage"\ndependencies = ["swarm-models", "asyncpg>=0.29"]\n'
        assert self.violations_of(tmp_path, project) == []

    def test_a_version_specifier_and_an_extra_still_name_the_dependency(self, tmp_path: Path) -> None:
        project = "[project]\ndependencies = [\"swarm_models[x]>=1; python_version>='3.12'\"]\n"
        assert self.violations_of(tmp_path, project) == []

    def test_a_missing_dependency_is_reported(self, tmp_path: Path) -> None:
        found = self.violations_of(tmp_path, '[project]\ndependencies = ["asyncpg"]\n')
        assert len(found) == 1
        assert "swarm_models" in found[0]
        assert "does not declare" in found[0]

    def test_an_unused_dependency_is_reported(self, tmp_path: Path) -> None:
        project = '[project]\ndependencies = ["swarm-models", "swarm-lifecycle"]\n'
        found = self.violations_of(tmp_path, project)
        assert len(found) == 1
        assert "swarm_lifecycle" in found[0]
        assert "no import needs" in found[0]

    def test_an_optional_dependency_counts_as_declared(self, tmp_path: Path) -> None:
        project = '[project]\ndependencies = []\n[project.optional-dependencies]\nfleet = ["swarm-models"]\n'
        assert self.violations_of(tmp_path, project) == []

    def test_a_layer_without_a_project_file_is_reported(self, tmp_path: Path) -> None:
        write_files(tmp_path, self.BASE)
        found = PackageDependencies().violations(tmp_path)
        assert len(found) == 1
        assert "swarm-storage" in found[0]
        assert "no pyproject.toml" in found[0]

    def test_a_kernel_lib_is_not_checked(self, tmp_path: Path) -> None:
        write_files(tmp_path, {"backend/libs/swarm-web/src/swarm_web/a.py": "from swarm_lifecycle.m import Y\n"})
        assert PackageDependencies().violations(tmp_path) == []
