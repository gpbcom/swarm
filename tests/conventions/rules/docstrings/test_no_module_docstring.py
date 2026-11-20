from __future__ import annotations

# Standard library imports
from pathlib import Path
from typing import ClassVar, Dict, List

# First-party imports
from tests.conventions.helpers import write_files
from tests.conventions.rules.docstrings.no_module_docstring import NoModuleDocstring
from tests.conventions.rules.service_tree import ServiceTree


class TestNoModuleDocstring:
    WORK_PATH: ClassVar[str] = "src/sample/service/work.py"
    INIT_PATH: ClassVar[str] = "src/sample/__init__.py"
    TEST_PATH: ClassVar[str] = "tests/test_work.py"
    CLASS_ONLY: ClassVar[str] = 'from __future__ import annotations\n\n\nclass Work:\n    """A piece of work."""\n'

    def violations(self, tmp_path: Path, files: Dict[str, str]) -> List[str]:
        write_files(tmp_path / "services" / "sample", files)
        return NoModuleDocstring().violations(ServiceTree(tmp_path / "services" / "sample"))

    def test_the_rule_is_named_no_module_docstring(self) -> None:
        assert NoModuleDocstring.NAME == "no_module_docstring"

    def test_a_file_that_starts_with_a_docstring_is_one_violation(self, tmp_path: Path) -> None:
        found = self.violations(tmp_path, {self.WORK_PATH: '"""The work."""\n\n' + self.CLASS_ONLY})
        assert len(found) == 1
        assert found[0].startswith("sample/src/sample/service/work.py:1:")

    def test_an_init_file_with_only_a_docstring_is_a_violation(self, tmp_path: Path) -> None:
        assert len(self.violations(tmp_path, {self.INIT_PATH: '"""The sample package."""\n'})) == 1

    def test_a_test_file_with_a_docstring_is_a_violation(self, tmp_path: Path) -> None:
        found = self.violations(tmp_path, {self.TEST_PATH: '"""Tests of the work."""\n'})
        assert len(found) == 1
        assert "sample/tests/test_work.py" in found[0]

    def test_a_class_docstring_is_not_a_module_docstring(self, tmp_path: Path) -> None:
        assert self.violations(tmp_path, {self.WORK_PATH: self.CLASS_ONLY}) == []

    def test_an_empty_file_is_not_reported(self, tmp_path: Path) -> None:
        assert self.violations(tmp_path, {self.INIT_PATH: ""}) == []
