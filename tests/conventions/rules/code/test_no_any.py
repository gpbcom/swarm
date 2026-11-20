from __future__ import annotations

# Standard library imports
from pathlib import Path
from typing import ClassVar, Dict, List

# Third-party imports
import pytest

# First-party imports
from tests.conventions.helpers import write_files
from tests.conventions.rules.code.no_any import NoAny
from tests.conventions.rules.service_tree import ServiceTree


class TestNoAny:
    WORK_PATH: ClassVar[str] = "src/sample/service/work.py"
    TEST_PATH: ClassVar[str] = "tests/test_work.py"

    def violations(self, tmp_path: Path, files: Dict[str, str]) -> List[str]:
        write_files(tmp_path / "services" / "sample", files)
        return NoAny().violations(ServiceTree(tmp_path / "services" / "sample"))

    def test_the_rule_is_named_no_any(self) -> None:
        assert NoAny.NAME == "no_any"

    def test_an_import_used_in_two_annotations_is_one_violation(self, tmp_path: Path) -> None:
        source = "from typing import Any\n\n\ndef f(a: Any) -> Any:\n    return a\n"
        found = self.violations(tmp_path, {self.WORK_PATH: source})
        assert len(found) == 1
        assert found[0].startswith("sample/src/sample/service/work.py:1:")

    def test_an_import_beside_other_names_is_one_violation(self, tmp_path: Path) -> None:
        found = self.violations(tmp_path, {self.WORK_PATH: "from typing import List, Any\n"})
        assert len(found) == 1

    def test_an_aliased_import_is_one_violation(self, tmp_path: Path) -> None:
        found = self.violations(tmp_path, {self.WORK_PATH: "from typing import Any as Anything\n"})
        assert len(found) == 1

    def test_an_import_from_typing_extensions_is_one_violation(self, tmp_path: Path) -> None:
        found = self.violations(tmp_path, {self.WORK_PATH: "from typing_extensions import Any\n"})
        assert len(found) == 1

    @pytest.mark.parametrize("module", ["typing", "typing_extensions"])
    def test_an_attribute_access_is_one_violation(self, tmp_path: Path, module: str) -> None:
        source = f"import {module}\n\nx: {module}.Any = 1\n"
        found = self.violations(tmp_path, {self.WORK_PATH: source})
        assert len(found) == 1
        assert ":3:" in found[0]

    def test_the_word_in_a_string_or_a_comment_is_not_reported(self, tmp_path: Path) -> None:
        source = 'from typing import List\n\n# Any value goes.\nx: List[str] = ["Any"]\n'
        assert self.violations(tmp_path, {self.WORK_PATH: source}) == []

    def test_a_file_under_tests_is_reported(self, tmp_path: Path) -> None:
        found = self.violations(tmp_path, {self.TEST_PATH: "from typing import Any\n"})
        assert len(found) == 1
        assert "sample/tests/test_work.py" in found[0]

    def test_a_clean_service_has_no_violation(self, tmp_path: Path) -> None:
        source = "from typing import List\n\nx: List[int] = []\n"
        files = {self.WORK_PATH: source, self.TEST_PATH: source}
        assert self.violations(tmp_path, files) == []
