from __future__ import annotations

from pathlib import Path
from typing import ClassVar, Dict, List

from tests.conventions.helpers import write_files
from tests.conventions.rules.code.no_nested_function import NoNestedFunction
from tests.conventions.rules.service_tree import ServiceTree


class TestNoNestedFunction:
    WORK_PATH: ClassVar[str] = "src/sample/service/work.py"
    TEST_PATH: ClassVar[str] = "tests/test_work.py"

    def violations(self, tmp_path: Path, files: Dict[str, str]) -> List[str]:
        write_files(tmp_path / "services" / "sample", files)
        return NoNestedFunction().violations(ServiceTree(tmp_path / "services" / "sample"))

    def test_the_rule_is_named_no_nested_function(self) -> None:
        assert NoNestedFunction.NAME == "no_nested_function"

    def test_a_function_inside_a_function_is_one_violation(self, tmp_path: Path) -> None:
        source = "def outer() -> None:\n    def inner() -> None:\n        pass\n"
        found = self.violations(tmp_path, {self.WORK_PATH: source})
        assert len(found) == 1
        assert found[0].startswith("sample/src/sample/service/work.py:2:")

    def test_an_async_function_inside_a_method_is_one_violation(self, tmp_path: Path) -> None:
        source = "class Work:\n    def run(self) -> None:\n        async def inner() -> None:\n            pass\n"
        found = self.violations(tmp_path, {self.WORK_PATH: source})
        assert len(found) == 1
        assert ":3:" in found[0]

    def test_three_levels_make_two_violations(self, tmp_path: Path) -> None:
        source = "def c() -> None:\n    def b() -> None:\n        def a() -> None:\n            pass\n"
        assert len(self.violations(tmp_path, {self.WORK_PATH: source})) == 2

    def test_methods_of_a_module_level_class_are_not_reported(self, tmp_path: Path) -> None:
        source = (
            "class Work:\n    def one(self) -> None:\n        pass\n\n    async def two(self) -> None:\n        pass\n"
        )
        assert self.violations(tmp_path, {self.WORK_PATH: source}) == []

    def test_a_class_defined_in_a_function_and_its_methods_are_not_reported(self, tmp_path: Path) -> None:
        source = "def outer() -> None:\n    class Inner:\n        def method(self) -> None:\n            pass\n"
        assert self.violations(tmp_path, {self.WORK_PATH: source}) == []

    def test_a_lambda_inside_a_function_is_not_reported(self, tmp_path: Path) -> None:
        source = "def outer() -> int:\n    return (lambda: 1)()\n"
        assert self.violations(tmp_path, {self.WORK_PATH: source}) == []

    def test_a_file_under_tests_is_reported(self, tmp_path: Path) -> None:
        source = "def outer() -> None:\n    def inner() -> None:\n        pass\n"
        found = self.violations(tmp_path, {self.TEST_PATH: source})
        assert len(found) == 1
        assert "sample/tests/test_work.py" in found[0]
