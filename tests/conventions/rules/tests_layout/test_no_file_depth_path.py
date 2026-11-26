from __future__ import annotations

# Standard library imports
from pathlib import Path
from typing import List

# Third-party imports
import pytest

# First-party imports
from tests.conventions.helpers import write_files
from tests.conventions.rules.tests_layout.no_file_depth_path import NoFileDepthPath


class TestNoFileDepthPath:
    FILE: str = "backend/apps/gateway/src/swarm_gateway/main.py"

    def violations_of(self, tmp_path: Path, source: str) -> List[str]:
        write_files(tmp_path, {self.FILE: source})
        return NoFileDepthPath().violations(tmp_path)

    def test_the_rule_has_its_name(self) -> None:
        assert NoFileDepthPath.NAME == "no_file_depth_path"

    @pytest.mark.parametrize(
        "source",
        [
            "from pathlib import Path\nROOT = Path(__file__).parents[3]\n",
            "from pathlib import Path\nROOT = Path(__file__).resolve().parents[1] / 'conf'\n",
            "from pathlib import Path\nfor parent in Path(__file__).parents:\n    pass\n",
        ],
    )
    def test_a_parents_lookup_from_file_is_reported(self, tmp_path: Path, source: str) -> None:
        found = self.violations_of(tmp_path, source)
        assert len(found) == 1
        assert self.FILE in found[0]

    def test_a_folder_passed_in_is_accepted(self, tmp_path: Path) -> None:
        source = (
            "import os\nfrom pathlib import Path\nROOT = Path(os.environ['SWARM_APP_ROOT'])\nUP = ROOT.parents[0]\n"
        )
        assert self.violations_of(tmp_path, source) == []

    def test_a_root_without_backend_has_no_violation(self, tmp_path: Path) -> None:
        assert NoFileDepthPath().violations(tmp_path) == []
