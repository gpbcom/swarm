from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import pytest

from tests.conventions.helpers import write_files
from tests.conventions.rules.files.one_class_per_file import OneClassPerFile
from tests.conventions.rules.service_tree import ServiceTree


class TestOneClassPerFile:
    def violations_of(self, tmp_path: Path, files: Dict[str, str]) -> List[str]:
        root = tmp_path / "services" / "sample"
        write_files(root, files)
        return OneClassPerFile().violations(ServiceTree(root))

    def test_the_rule_has_its_name(self) -> None:
        assert OneClassPerFile.NAME == "one_class_per_file"

    def test_a_file_with_one_class_is_accepted(self, tmp_path: Path) -> None:
        files = {"src/sample/service/a.py": "class A:\n    pass\n"}
        assert self.violations_of(tmp_path, files) == []

    @pytest.mark.parametrize("count", [2, 3])
    def test_a_file_with_several_classes_gives_one_violation(self, tmp_path: Path, count: int) -> None:
        body = "".join(f"class C{index}:\n    pass\n\n" for index in range(count))
        found = self.violations_of(tmp_path, {"src/sample/service/many.py": body})
        assert len(found) == 1
        assert found[0].startswith("sample/src/sample/service/many.py:4:")

    def test_an_enum_and_an_exception_together_are_refused(self, tmp_path: Path) -> None:
        body = (
            "from enum import Enum\n\n\n"
            "class Colour(Enum):\n    RED = 1\n\n\n"
            "class SEColourError(Exception):\n    pass\n"
        )
        found = self.violations_of(tmp_path, {"src/sample/models/mixed.py": body})
        assert len(found) == 1
        assert "mixed.py" in found[0]

    def test_a_nested_class_is_accepted(self, tmp_path: Path) -> None:
        body = "class Outer:\n    class Inner:\n        pass\n"
        assert self.violations_of(tmp_path, {"src/sample/models/outer.py": body}) == []

    def test_a_violating_test_file_is_reported(self, tmp_path: Path) -> None:
        body = "class TestA:\n    pass\n\n\nclass TestB:\n    pass\n"
        found = self.violations_of(tmp_path, {"tests/test_two.py": body})
        assert len(found) == 1
        assert "tests/test_two.py" in found[0]

    def test_a_clean_service_has_no_violation(self, tmp_path: Path) -> None:
        files = {
            "src/sample/api/a.py": "class A:\n    pass\n",
            "src/sample/service/b.py": "class B:\n    pass\n",
            "tests/test_b.py": "class TestB:\n    pass\n",
        }
        assert self.violations_of(tmp_path, files) == []

    def test_a_service_without_src_has_no_violation(self, tmp_path: Path) -> None:
        assert self.violations_of(tmp_path, {"tests/test_a.py": "class TestA:\n    pass\n"}) == []
