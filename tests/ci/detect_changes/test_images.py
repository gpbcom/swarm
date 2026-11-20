from __future__ import annotations

from pathlib import Path
from typing import ClassVar, List

import pytest

from tests.ci.detect_changes.helpers import ALL_IMAGES, IMAGES_KEY, SERVICES_KEY, outputs, run_detector, write_repo


class TestImages:
    ALPHA: ClassVar[str] = '["services/alpha"]'
    GROUND_CONTROL: ClassVar[str] = '["frontends/ground-control"]'
    TWO_FOLDERS: ClassVar[str] = '["frontends/ground-control","services/alpha"]'
    EMPTY: ClassVar[str] = "[]"

    def detect(self, tmp_path: Path, changed: List[str], *args: str) -> str:
        write_repo(tmp_path)
        result = run_detector(tmp_path, changed, *args)
        assert result.returncode == 0, result.stderr
        return outputs(result)[IMAGES_KEY]

    def test_a_service_with_a_dockerfile_is_listed(self, tmp_path: Path) -> None:
        assert self.detect(tmp_path, ["services/alpha/src/alpha/main.py"]) == self.ALPHA

    def test_a_service_without_a_dockerfile_is_not_listed_but_is_still_selected(self, tmp_path: Path) -> None:
        write_repo(tmp_path)
        result = run_detector(tmp_path, ["services/beta/src/beta/main.py"])
        values = outputs(result)
        assert values[IMAGES_KEY] == self.EMPTY
        assert values[SERVICES_KEY] == '["beta"]'

    def test_a_front_end_with_a_dockerfile_is_listed(self, tmp_path: Path) -> None:
        assert self.detect(tmp_path, ["frontends/ground-control/src/main.ts"]) == self.GROUND_CONTROL

    def test_a_front_end_without_a_package_is_listed_when_it_has_a_dockerfile(self, tmp_path: Path) -> None:
        assert self.detect(tmp_path, ["frontends/notes/x.ts"]) == '["frontends/notes"]'

    @pytest.mark.parametrize("path", ["services/alpha/Dockerfile", "services/alpha/.dockerignore"])
    def test_a_change_to_the_dockerfile_of_a_service_lists_its_image(self, tmp_path: Path, path: str) -> None:
        assert self.detect(tmp_path, [path]) == self.ALPHA

    def test_a_change_to_the_dockerfile_of_a_front_end_lists_its_image(self, tmp_path: Path) -> None:
        assert self.detect(tmp_path, ["frontends/ground-control/Dockerfile"]) == self.GROUND_CONTROL

    def test_two_folders_are_listed_sorted_and_once_each(self, tmp_path: Path) -> None:
        changed = ["services/alpha/a.py", "frontends/ground-control/a.ts", "services/alpha/b.py"]
        assert self.detect(tmp_path, changed) == self.TWO_FOLDERS

    @pytest.mark.parametrize("path", ["services/gone/x.py", "services/_template/x.py", "frontends/.hidden/x.ts"])
    def test_a_folder_that_is_not_discovered_is_not_listed(self, tmp_path: Path, path: str) -> None:
        assert self.detect(tmp_path, [path]) == self.EMPTY

    def test_all_lists_every_image_folder_with_empty_stdin(self, tmp_path: Path) -> None:
        assert self.detect(tmp_path, [], "--all") == ALL_IMAGES
