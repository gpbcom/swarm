from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import pytest

from tests.conventions.helpers import write_files
from tests.conventions.rules.files.five_files_per_folder import FiveFilesPerFolder
from tests.conventions.rules.service_tree import ServiceTree


class TestFiveFilesPerFolder:
    def violations_of(self, tmp_path: Path, files: Dict[str, str]) -> List[str]:
        root = tmp_path / "services" / "sample"
        write_files(root, files)
        return FiveFilesPerFolder().violations(ServiceTree(root))

    def numbered(self, folder: str, count: int) -> Dict[str, str]:
        return {f"{folder}/module_{index}.py": "" for index in range(count)}

    def test_the_rule_has_its_name(self) -> None:
        assert FiveFilesPerFolder.NAME == "five_files_per_folder"

    def test_five_files_are_accepted(self, tmp_path: Path) -> None:
        assert self.violations_of(tmp_path, self.numbered("src/sample/service", 5)) == []

    def test_six_files_give_one_violation_naming_the_folder(self, tmp_path: Path) -> None:
        found = self.violations_of(tmp_path, self.numbered("src/sample/service", 6))
        assert len(found) == 1
        assert "sample/src/sample/service" in found[0]

    @pytest.mark.parametrize("extra", [["__init__.py"], ["conftest.py"], ["__init__.py", "conftest.py"]])
    def test_init_and_conftest_files_are_not_counted(self, tmp_path: Path, extra: List[str]) -> None:
        files = self.numbered("src/sample/service", 5)
        files.update({f"src/sample/service/{name}": "" for name in extra})
        assert self.violations_of(tmp_path, files) == []

    def test_a_crowded_sub_folder_is_reported_alone(self, tmp_path: Path) -> None:
        files = self.numbered("src/sample/service/deep", 6)
        files["src/sample/service/top.py"] = ""
        found = self.violations_of(tmp_path, files)
        assert len(found) == 1
        assert "service/deep" in found[0]

    def test_a_crowded_tests_folder_is_reported(self, tmp_path: Path) -> None:
        found = self.violations_of(tmp_path, self.numbered("tests/service", 6))
        assert len(found) == 1
        assert "tests/service" in found[0]
