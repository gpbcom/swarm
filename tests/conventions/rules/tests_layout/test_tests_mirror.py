from __future__ import annotations

# Standard library imports
from pathlib import Path
from typing import ClassVar, Dict, List

# First-party imports
from tests.conventions.helpers import write_files
from tests.conventions.rules.tests_layout.tests_mirror import TestsMirror


class TestTestsMirror:
    SOURCES: ClassVar[Dict[str, str]] = {
        "backend/swarm-service/src/swarm_service/fleet/drone_service.py": "",
        "backend/swarm-service/src/swarm_service/fleet/bus/handler.py": "",
        "backend/apps/gateway/src/swarm_gateway/main.py": "",
    }

    def violations_of(self, tmp_path: Path, tests: Dict[str, str]) -> List[str]:
        write_files(tmp_path, self.SOURCES)
        write_files(tmp_path, tests)
        return TestsMirror().violations(tmp_path)

    def test_the_rule_has_its_name(self) -> None:
        assert TestsMirror.NAME == "tests_mirror"

    def test_a_mirrored_tree_is_accepted(self, tmp_path: Path) -> None:
        tests = {
            "tests/swarm_service/fleet/test_drone_service.py": "",
            "tests/swarm_service/fleet/bus/test_handler.py": "",
            "tests/swarm_gateway/test_main.py": "",
            "tests/swarm_service/fleet/helpers.py": "",
        }
        assert self.violations_of(tmp_path, tests) == []

    def test_a_folder_named_after_a_source_file_is_accepted(self, tmp_path: Path) -> None:
        tests = {"tests/swarm_service/fleet/drone_service/test_create.py": ""}
        assert self.violations_of(tmp_path, tests) == []

    def test_a_prefix_that_keeps_the_test_name_unique_is_accepted(self, tmp_path: Path) -> None:
        tests = {"tests/swarm_service/fleet/test_swarm_service_drone_service.py": ""}
        assert self.violations_of(tmp_path, tests) == []

    def test_a_prefixed_name_still_needs_its_source_file(self, tmp_path: Path) -> None:
        found = self.violations_of(tmp_path, {"tests/swarm_service/fleet/test_swarm_service_ghost.py": ""})
        assert len(found) == 1

    def test_a_folder_without_counterpart_is_reported(self, tmp_path: Path) -> None:
        found = self.violations_of(tmp_path, {"tests/swarm_service/ghost/test_x.py": ""})
        assert len(found) == 1
        assert "The folder ghost has no counterpart" in found[0]

    def test_a_test_without_source_is_reported(self, tmp_path: Path) -> None:
        found = self.violations_of(tmp_path, {"tests/swarm_service/fleet/test_missing.py": ""})
        assert len(found) == 1
        assert "No missing.py" in found[0]

    def test_an_unknown_module_folder_is_reported(self, tmp_path: Path) -> None:
        found = self.violations_of(tmp_path, {"tests/swarm_nothing/test_x.py": ""})
        assert len(found) == 1
        assert "mirrors no package" in found[0]

    def test_folders_outside_the_module_names_are_free(self, tmp_path: Path) -> None:
        tests = {"tests/fakes/mavlink/test_x.py": "", "tests/conventions/test_y.py": "", "tests/conftest.py": ""}
        assert self.violations_of(tmp_path, tests) == []
