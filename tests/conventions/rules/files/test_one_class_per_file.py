from __future__ import annotations

# Standard library imports
from pathlib import Path
from typing import ClassVar, Dict, List

# Third-party imports
import pytest

# First-party imports
from tests.conventions.helpers import write_files
from tests.conventions.rules.files.one_class_per_file import OneClassPerFile
from tests.conventions.rules.service_tree import ServiceTree


class TestOneClassPerFile:
    ONE_CLASS: ClassVar[Dict[str, str]] = {"src/sample/service/a.py": "class A:\n    pass\n"}
    MANY_PATH: ClassVar[str] = "src/sample/service/many.py"
    MIXED_PATH: ClassVar[str] = "src/sample/models/mixed.py"
    OUTER_PATH: ClassVar[str] = "src/sample/models/outer.py"
    TWO_TEST_CLASSES_PATH: ClassVar[str] = "tests/test_two.py"
    CLEAN_SERVICE: ClassVar[Dict[str, str]] = {
        "src/sample/api/a.py": "class A:\n    pass\n",
        "src/sample/service/b.py": "class B:\n    pass\n",
        "tests/test_b.py": "class TestB:\n    pass\n",
    }
    TESTS_ONLY: ClassVar[Dict[str, str]] = {"tests/test_a.py": "class TestA:\n    pass\n"}
    ENUMS_PATH: ClassVar[str] = "src/sample/models/enums.py"
    TWO_ENUMS: ClassVar[str] = (
        "from enum import StrEnum, unique\n\n\n"
        '@unique\nclass Colour(StrEnum):\n    RED = "red"\n\n\n'
        '@unique\nclass Shape(StrEnum):\n    ROUND = "round"\n'
    )
    ENUM_AND_MODEL: ClassVar[str] = (
        "import enum\n\nfrom pydantic import BaseModel\n\n\n"
        'class Colour(enum.StrEnum):\n    RED = "red"\n\n\n'
        "class Paint(BaseModel):\n    colour: Colour\n"
    )
    TWO_ENUMS_ELSEWHERE_PATH: ClassVar[str] = "src/sample/models/colours.py"

    def violations_of(self, tmp_path: Path, files: Dict[str, str]) -> List[str]:
        root = tmp_path / "services" / "sample"
        write_files(root, files)
        return OneClassPerFile().violations(ServiceTree(root))

    def test_the_rule_has_its_name(self) -> None:
        assert OneClassPerFile.NAME == "one_class_per_file"

    def test_a_file_with_one_class_is_accepted(self, tmp_path: Path) -> None:
        assert self.violations_of(tmp_path, self.ONE_CLASS) == []

    @pytest.mark.parametrize("count", [2, 3])
    def test_a_file_with_several_classes_gives_one_violation(self, tmp_path: Path, count: int) -> None:
        body = "".join(f"class C{index}:\n    pass\n\n" for index in range(count))
        found = self.violations_of(tmp_path, {self.MANY_PATH: body})
        assert len(found) == 1
        assert found[0].startswith("sample/src/sample/service/many.py:4:")

    def test_an_enum_and_an_exception_together_are_refused(self, tmp_path: Path) -> None:
        body = (
            "from enum import Enum\n\n\n"
            "class Colour(Enum):\n    RED = 1\n\n\n"
            "class SEColourError(Exception):\n    pass\n"
        )
        found = self.violations_of(tmp_path, {self.MIXED_PATH: body})
        assert len(found) == 1
        assert "mixed.py" in found[0]

    def test_several_enums_in_enums_py_are_accepted(self, tmp_path: Path) -> None:
        write_files(tmp_path, {self.ENUMS_PATH: self.TWO_ENUMS})
        assert OneClassPerFile().violations(ServiceTree(tmp_path)) == []

    def test_an_enum_and_another_class_in_enums_py_are_refused(self, tmp_path: Path) -> None:
        write_files(tmp_path, {self.ENUMS_PATH: self.ENUM_AND_MODEL})
        assert len(OneClassPerFile().violations(ServiceTree(tmp_path))) == 1

    def test_several_enums_outside_enums_py_are_refused(self, tmp_path: Path) -> None:
        write_files(tmp_path, {self.TWO_ENUMS_ELSEWHERE_PATH: self.TWO_ENUMS})
        assert len(OneClassPerFile().violations(ServiceTree(tmp_path))) == 1

    def test_a_nested_class_is_accepted(self, tmp_path: Path) -> None:
        body = "class Outer:\n    class Inner:\n        pass\n"
        assert self.violations_of(tmp_path, {self.OUTER_PATH: body}) == []

    def test_a_violating_test_file_is_reported(self, tmp_path: Path) -> None:
        body = "class TestA:\n    pass\n\n\nclass TestB:\n    pass\n"
        found = self.violations_of(tmp_path, {self.TWO_TEST_CLASSES_PATH: body})
        assert len(found) == 1
        assert "tests/test_two.py" in found[0]

    def test_a_clean_service_has_no_violation(self, tmp_path: Path) -> None:
        assert self.violations_of(tmp_path, self.CLEAN_SERVICE) == []

    def test_a_service_without_src_has_no_violation(self, tmp_path: Path) -> None:
        assert self.violations_of(tmp_path, self.TESTS_ONLY) == []
