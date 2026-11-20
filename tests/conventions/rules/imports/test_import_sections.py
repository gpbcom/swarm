from __future__ import annotations

# Standard library imports
from pathlib import Path
from typing import ClassVar, Dict, List

# Third-party imports
import pytest

# First-party imports
from tests.conventions.helpers import write_files
from tests.conventions.rules.imports.import_sections import ImportSections
from tests.conventions.rules.service_tree import ServiceTree


class TestImportSections:
    WORK_PATH: ClassVar[str] = "src/sample/service/work.py"
    TEST_PATH: ClassVar[str] = "tests/test_work.py"
    INIT_PATH: ClassVar[str] = "src/sample/__init__.py"
    FUTURE: ClassVar[str] = "from __future__ import annotations\n\n"
    GOOD: ClassVar[str] = (
        "from __future__ import annotations\n\n# Standard library imports\nimport os\nfrom typing import List\n\n"
        "# Third-party imports\nimport yaml\n\n# First-party imports\nfrom sample.models.enums import Kind\n"
        "from tests.helpers import a_kind\n"
    )

    def violations(self, tmp_path: Path, files: Dict[str, str]) -> List[str]:
        write_files(tmp_path / "services" / "sample", files)
        return ImportSections().violations(ServiceTree(tmp_path / "services" / "sample"))

    def test_the_rule_is_named_import_sections(self) -> None:
        assert ImportSections.NAME == "import_sections"

    def test_three_sections_in_order_under_their_comments_pass(self, tmp_path: Path) -> None:
        assert self.violations(tmp_path, {self.WORK_PATH: self.GOOD, self.TEST_PATH: self.GOOD}) == []

    @pytest.mark.parametrize(
        "source",
        [
            "import os\n",
            "# Third-party imports\nimport os\n",
            "# Standard library imports\nimport yaml\n",
            "# Third-party imports\nfrom sample.models.enums import Kind\n",
            "# Standard library imports\nimport os\n\nfrom sample.models.enums import Kind\n",
        ],
    )
    def test_an_import_outside_its_section_is_a_violation(self, tmp_path: Path, source: str) -> None:
        found = self.violations(tmp_path, {self.WORK_PATH: self.FUTURE + source})
        assert len(found) == 1
        assert found[0].startswith("sample/src/sample/service/work.py:")

    def test_sections_out_of_order_are_a_violation(self, tmp_path: Path) -> None:
        source = (
            "# First-party imports\nfrom sample.models.enums import Kind\n\n# Standard library imports\nimport os\n"
        )
        found = self.violations(tmp_path, {self.WORK_PATH: self.FUTURE + source})
        assert any("out of order" in message for message in found)

    def test_a_test_file_is_checked_too(self, tmp_path: Path) -> None:
        assert len(self.violations(tmp_path, {self.TEST_PATH: self.FUTURE + "import pytest\n"})) == 1

    def test_an_init_file_is_not_checked(self, tmp_path: Path) -> None:
        assert self.violations(tmp_path, {self.INIT_PATH: self.FUTURE + "from sample.work import Work\n"}) == []

    def test_an_import_kept_in_its_section_with_isort_skip_passes(self, tmp_path: Path) -> None:
        source = "# First-party imports\nfrom sample.models.enums import Kind  # isort: skip\n"
        assert self.violations(tmp_path, {self.WORK_PATH: self.FUTURE + source}) == []
