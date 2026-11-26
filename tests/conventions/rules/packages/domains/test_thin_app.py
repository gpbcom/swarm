from __future__ import annotations

# Standard library imports
from pathlib import Path
from typing import Dict, List

# Third-party imports
import pytest

# First-party imports
from tests.conventions.helpers import write_files
from tests.conventions.rules.packages.domains.thin_app import ThinApp


class TestThinApp:
    APP: str = "backend/apps/gateway/src/swarm_gateway"

    def violations_of(self, tmp_path: Path, files: Dict[str, str]) -> List[str]:
        write_files(tmp_path, files)
        return ThinApp().violations(tmp_path)

    def test_the_rule_has_its_name(self) -> None:
        assert ThinApp.NAME == "thin_app"

    def test_a_main_without_argument_is_accepted(self, tmp_path: Path) -> None:
        files = {f"{self.APP}/main.py": "def main() -> None:\n    pass\n", f"{self.APP}/__init__.py": ""}
        assert self.violations_of(tmp_path, files) == []

    @pytest.mark.parametrize("signature", ["x", "*args", "**kwargs", "*, flag=1"])
    def test_a_main_with_an_argument_is_reported(self, tmp_path: Path, signature: str) -> None:
        found = self.violations_of(tmp_path, {f"{self.APP}/main.py": f"def main({signature}) -> None:\n    pass\n"})
        assert len(found) == 1
        assert "no argument" in found[0]

    def test_a_file_without_main_is_reported(self, tmp_path: Path) -> None:
        found = self.violations_of(tmp_path, {f"{self.APP}/main.py": "VALUE = 1\n"})
        assert len(found) == 1
        assert "no main() function" in found[0]

    def test_another_file_or_folder_is_reported(self, tmp_path: Path) -> None:
        files = {
            f"{self.APP}/main.py": "def main() -> None:\n    pass\n",
            f"{self.APP}/settings.py": "",
            f"{self.APP}/service/a.py": "",
        }
        found = self.violations_of(tmp_path, files)
        assert len(found) == 2
        assert any("settings.py" in message for message in found)
        assert any("service" in message for message in found)

    def test_an_app_without_main_is_reported(self, tmp_path: Path) -> None:
        found = self.violations_of(tmp_path, {f"{self.APP}/__init__.py": ""})
        assert len(found) == 1
        assert "no main.py" in found[0]

    def test_a_layer_package_is_not_an_app(self, tmp_path: Path) -> None:
        assert self.violations_of(tmp_path, {"backend/swarm-api/src/swarm_api/other.py": ""}) == []
