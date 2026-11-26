from __future__ import annotations

# Standard library imports
from pathlib import Path
from typing import ClassVar, Dict, List

# Third-party imports
import pytest

# First-party imports
from tests.conventions.helpers import write_files
from tests.conventions.rules.command_line.no_command_line import NoCommandLine
from tests.conventions.rules.service_tree import ServiceTree


class TestNoCommandLine:
    BACKEND_PATH: ClassVar[str] = "backend/swarm-service/src/swarm_service/work.py"
    SCRIPT_PATH: ClassVar[str] = "scripts/openapi/export.py"
    TEST_PATH: ClassVar[str] = "tests/swarm_gateway/test_main.py"

    def violations(self, tmp_path: Path, files: Dict[str, str]) -> List[str]:
        write_files(tmp_path, files)
        return NoCommandLine().violations(ServiceTree(tmp_path))

    def test_the_rule_is_named_no_command_line(self) -> None:
        assert NoCommandLine.NAME == "no_command_line"

    def test_a_repository_without_backend_or_scripts_has_no_violation(self, tmp_path: Path) -> None:
        assert self.violations(tmp_path, {"services/a/src/a/cli/main.py": "import argparse\n"}) == []

    def test_clean_code_has_no_violation(self, tmp_path: Path) -> None:
        files = {self.BACKEND_PATH: "import os\n", self.SCRIPT_PATH: "import sys\nsys.exit(0)\n"}
        assert self.violations(tmp_path, files) == []

    @pytest.mark.parametrize(
        "source",
        ["import argparse\n", "import click\n", "import typer.main\n", "from argparse import ArgumentParser\n"],
    )
    def test_a_command_line_library_is_refused_in_every_checked_folder(self, tmp_path: Path, source: str) -> None:
        files = {self.BACKEND_PATH: source, self.SCRIPT_PATH: source, self.TEST_PATH: source}
        assert len(self.violations(tmp_path, files)) == 3

    def test_sys_argv_is_refused_with_its_line(self, tmp_path: Path) -> None:
        found = self.violations(tmp_path, {self.SCRIPT_PATH: "import sys\n\nvalue = sys.argv[1]\n"})
        assert len(found) == 1
        assert ":3:" in found[0]

    def test_an_argv_imported_from_sys_is_refused(self, tmp_path: Path) -> None:
        assert len(self.violations(tmp_path, {self.SCRIPT_PATH: "from sys import argv\n"})) == 1

    def test_another_argv_attribute_is_allowed(self, tmp_path: Path) -> None:
        assert self.violations(tmp_path, {self.SCRIPT_PATH: "value = settings.argv\n"}) == []

    @pytest.mark.parametrize(
        "path",
        [
            "backend/swarm-service/src/swarm_service/cli/run.py",
            "backend/swarm-api/src/swarm_api/commands/run.py",
            "backend/apps/gateway/src/swarm_gateway/commands/run.py",
        ],
    )
    def test_a_command_line_folder_is_refused(self, tmp_path: Path, path: str) -> None:
        found = self.violations(tmp_path, {path: "x = 1\n"})
        assert len(found) == 1
        assert "Folder" in found[0]

    @pytest.mark.parametrize("path", ["scripts/cli.py", "backend/swarm-api/src/swarm_api/v1/commands.py"])
    def test_a_command_line_module_is_refused(self, tmp_path: Path, path: str) -> None:
        found = self.violations(tmp_path, {path: "x = 1\n"})
        assert len(found) == 1
        assert "Module" in found[0]

    def test_the_commands_domain_outside_the_api_layer_is_allowed(self, tmp_path: Path) -> None:
        files = {
            "backend/swarm-models/src/swarm_models/commands/command.py": "x = 1\n",
            "tests/swarm_models/commands/test_command.py": "x = 1\n",
        }
        assert self.violations(tmp_path, files) == []

    def test_the_test_mirrors_are_checked_and_other_tests_are_not(self, tmp_path: Path) -> None:
        files = {
            "tests/scripts/test_export.py": "import argparse\n",
            "tests/swarm_gateway/cli/test_x.py": "x = 1\n",
            "tests/harness/test_tool.py": "import argparse\n",
        }
        assert len(self.violations(tmp_path, files)) == 2
