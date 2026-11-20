from __future__ import annotations

from pathlib import Path
from typing import ClassVar, Dict, List

import pytest

from tests.conventions.helpers import write_files
from tests.conventions.rules.classes.lifecycle_base_classes import LifecycleBaseClasses
from tests.conventions.rules.service_tree import ServiceTree


class TestLifecycleBaseClasses:
    JOB_PATH: ClassVar[str] = "src/sample/service/job.py"
    RUNNABLE_PATH: ClassVar[str] = "src/sample/runnables/runnable.py"
    MODELS_JOB_PATH: ClassVar[str] = "src/sample/models/job.py"
    TESTS_JOB_PATH: ClassVar[str] = "tests/service/job.py"
    JOB_WITH_RUNNABLE_BASE: ClassVar[Dict[str, str]] = {
        "src/sample/service/base_job.py": "class BaseJob(Runnable):\n    pass\n",
        "src/sample/service/job.py": "class Job(BaseJob):\n    def run(self) -> None: ...\n",
    }
    JOB_BESIDE_RUNNABLE: ClassVar[Dict[str, str]] = {
        "src/sample/runnables/runnable.py": "class Runnable(ABC):\n    def run(self) -> None: ...\n",
        "src/sample/service/job.py": "class Job(Runnable):\n    def run(self) -> None: ...\n",
    }

    def violations(self, tmp_path: Path, files: Dict[str, str]) -> List[str]:
        root = tmp_path / "services" / "sample"
        write_files(root, files)
        return LifecycleBaseClasses().violations(ServiceTree(root))

    def test_the_rule_has_a_name(self) -> None:
        assert LifecycleBaseClasses.NAME == "lifecycle_base_classes"

    @pytest.mark.parametrize(
        "source",
        [
            "class Job:\n    def run(self) -> None: ...\n",
            "class Job:\n    async def run(self) -> None: ...\n",
            "class Job(Runnable):\n    def start(self) -> None: ...\n",
            "class Job:\n    def start(self) -> None: ...\n    def stop(self) -> None: ...\n",
        ],
    )
    def test_a_misused_lifecycle_method_gives_one_violation(self, tmp_path: Path, source: str) -> None:
        found = self.violations(tmp_path, {self.JOB_PATH: source})
        assert len(found) == 1
        assert found[0].startswith("sample/src/sample/service/job.py:")

    @pytest.mark.parametrize(
        "source",
        [
            "class Job(Runnable):\n    def run(self) -> None: ...\n",
            "class Job(lifecycle.AsyncRunnable):\n    async def run(self) -> None: ...\n",
            "class Job:\n    def initialize(self) -> None: ...\n",
        ],
    )
    def test_a_correct_class_gives_no_violation(self, tmp_path: Path, source: str) -> None:
        assert self.violations(tmp_path, {self.JOB_PATH: source}) == []

    def test_a_base_class_of_the_service_that_is_runnable_is_followed(self, tmp_path: Path) -> None:
        assert self.violations(tmp_path, self.JOB_WITH_RUNNABLE_BASE) == []

    @pytest.mark.parametrize(
        "source",
        [
            "class Runnable(ABC):\n    def run(self) -> None: ...\n",
            "class AsyncRunnable(ABC):\n    async def run(self) -> None: ...\n",
        ],
    )
    def test_the_definition_of_a_lifecycle_base_class_gives_no_violation(self, tmp_path: Path, source: str) -> None:
        assert self.violations(tmp_path, {self.RUNNABLE_PATH: source}) == []

    def test_start_is_still_refused_in_the_definition_of_a_lifecycle_base_class(self, tmp_path: Path) -> None:
        source = "class Runnable:\n    def start(self) -> None: ...\n"
        found = self.violations(tmp_path, {self.RUNNABLE_PATH: source})
        assert len(found) == 1

    def test_a_subclass_beside_the_definition_of_runnable_gives_no_violation(self, tmp_path: Path) -> None:
        assert self.violations(tmp_path, self.JOB_BESIDE_RUNNABLE) == []

    def test_the_models_layer_is_not_checked(self, tmp_path: Path) -> None:
        source = "class Job:\n    def run(self) -> None: ...\n    def start(self) -> None: ...\n"
        assert self.violations(tmp_path, {self.MODELS_JOB_PATH: source}) == []

    def test_a_class_with_run_in_the_tests_gives_one_violation(self, tmp_path: Path) -> None:
        source = "class Job:\n    def run(self) -> None: ...\n"
        found = self.violations(tmp_path, {self.TESTS_JOB_PATH: source})
        assert len(found) == 1
