from __future__ import annotations

# Standard library imports
from pathlib import Path
from typing import ClassVar, List

# Third-party imports
import pytest

# First-party imports
from tests.ci.detect_changes.helpers import ALL_IMAGES, IMAGES_KEY, SERVICES_KEY, outputs, run_detector, write_repo


class TestImages:
    ALPHA: ClassVar[str] = '["backend/apps/alpha"]'
    GROUND_CONTROL: ClassVar[str] = '["frontend/apps/ground-control"]'
    TWO_FOLDERS: ClassVar[str] = '["backend/apps/alpha","frontend/apps/ground-control"]'
    EMPTY: ClassVar[str] = "[]"

    def detect(self, tmp_path: Path, changed: List[str], *args: str) -> str:
        write_repo(tmp_path)
        result = run_detector(tmp_path, changed, *args)
        assert result.returncode == 0, result.stderr
        return outputs(result)[IMAGES_KEY]

    def test_an_app_with_a_dockerfile_is_listed(self, tmp_path: Path) -> None:
        assert self.detect(tmp_path, ["backend/apps/alpha/src/swarm_alpha/main.py"]) == self.ALPHA

    def test_an_app_without_a_dockerfile_is_not_listed_but_is_still_selected(self, tmp_path: Path) -> None:
        write_repo(tmp_path)
        result = run_detector(tmp_path, ["backend/apps/beta/src/swarm_beta/main.py"])
        values = outputs(result)
        assert values[IMAGES_KEY] == self.EMPTY
        assert values[SERVICES_KEY] == '["beta"]'

    def test_a_front_end_with_a_dockerfile_is_listed(self, tmp_path: Path) -> None:
        assert self.detect(tmp_path, ["frontend/apps/ground-control/src/main.ts"]) == self.GROUND_CONTROL

    def test_a_front_end_without_a_package_is_listed_when_it_has_a_dockerfile(self, tmp_path: Path) -> None:
        assert self.detect(tmp_path, ["frontend/apps/notes/x.ts"]) == '["frontend/apps/notes"]'

    @pytest.mark.parametrize("path", ["backend/apps/alpha/Dockerfile", "backend/apps/alpha/.dockerignore"])
    def test_a_change_to_the_dockerfile_of_an_app_lists_its_image(self, tmp_path: Path, path: str) -> None:
        assert self.detect(tmp_path, [path]) == self.ALPHA

    def test_a_change_to_the_dockerfile_of_a_front_end_lists_its_image(self, tmp_path: Path) -> None:
        assert self.detect(tmp_path, ["frontend/apps/ground-control/Dockerfile"]) == self.GROUND_CONTROL

    def test_two_folders_are_listed_sorted_and_once_each(self, tmp_path: Path) -> None:
        changed = ["backend/apps/alpha/a.py", "frontend/apps/ground-control/a.ts", "backend/apps/alpha/b.py"]
        assert self.detect(tmp_path, changed) == self.TWO_FOLDERS

    @pytest.mark.parametrize(
        "path", ["backend/apps/gone/x.py", "backend/apps/_template/x.py", "frontend/apps/.hidden/x.ts"]
    )
    def test_a_folder_that_is_not_discovered_is_not_listed(self, tmp_path: Path, path: str) -> None:
        assert self.detect(tmp_path, [path]) == self.EMPTY

    def test_all_lists_every_image_folder_with_empty_stdin(self, tmp_path: Path) -> None:
        assert self.detect(tmp_path, [], "--all") == ALL_IMAGES
