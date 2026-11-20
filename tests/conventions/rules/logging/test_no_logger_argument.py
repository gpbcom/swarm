from __future__ import annotations

from pathlib import Path
from typing import ClassVar, Dict, List

import pytest

from tests.conventions.helpers import write_files
from tests.conventions.rules.logging.no_logger_argument import NoLoggerArgument
from tests.conventions.rules.service_tree import ServiceTree


class TestNoLoggerArgument:
    WORK_PATH: ClassVar[str] = "src/sample/service/work.py"
    TEST_PATH: ClassVar[str] = "tests/test_work.py"

    def violations(self, tmp_path: Path, files: Dict[str, str]) -> List[str]:
        write_files(tmp_path / "services" / "sample", files)
        return NoLoggerArgument().violations(ServiceTree(tmp_path / "services" / "sample"))

    def test_the_rule_is_named_no_logger_argument(self) -> None:
        assert NoLoggerArgument.NAME == "no_logger_argument"

    @pytest.mark.parametrize(
        "call",
        [
            "Work(config, self.logger)",
            "Work(config, logger=self.logger)",
            "Work(logger=logger)",
            "Work(getLogger('work'))",
            "factories.Work(config, logging.getLogger(__name__))",
            "cls(config, logger)",
        ],
    )
    def test_a_new_object_handed_a_logger_is_a_violation(self, tmp_path: Path, call: str) -> None:
        found = self.violations(tmp_path, {self.WORK_PATH: f"x = {call}\n"})
        assert len(found) == 1
        assert found[0].startswith("sample/src/sample/service/work.py:1:")

    @pytest.mark.parametrize(
        "call",
        [
            "Work(config)",
            "Work()",
            "super().__init__(config.status_interval_s, logger)",
            "self.logger.info('Built %s.', name)",
            "build(config, logger)",
        ],
    )
    def test_a_call_that_creates_nothing_or_hands_no_logger_is_not_reported(self, tmp_path: Path, call: str) -> None:
        assert self.violations(tmp_path, {self.WORK_PATH: f"x = {call}\n"}) == []

    def test_a_test_may_hand_a_logger(self, tmp_path: Path) -> None:
        assert self.violations(tmp_path, {self.TEST_PATH: "x = Work(logger=logger)\n"}) == []
