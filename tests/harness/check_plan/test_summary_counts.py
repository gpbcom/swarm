from __future__ import annotations

# Standard library imports
from pathlib import Path
from typing import Tuple

# Third-party imports
import pytest

# First-party imports
from tests.harness.check_plan.helpers import (
    AWAITING,
    TICKET_ID,
    json_block,
    plan_text,
    run_script,
    sample_tasks,
    write_plan_text,
)


class TestSummaryCounts:
    def run_with_summary(self, tmp_path: Path, summary: str, heading: str = "## Summary") -> Tuple[int, str]:
        body = f"{heading}\n\n{summary}\n\n## Assumptions\n\nThe 99 tasks of another plan.\n\n## Task graph\n\n"
        write_plan_text(tmp_path, plan_text(AWAITING, body + json_block(sample_tasks())))
        result = run_script(TICKET_ID, "--root", str(tmp_path))
        return result.returncode, result.stdout

    @pytest.mark.parametrize(
        "summary",
        [
            pytest.param("The graph has 7 tasks in 2 waves.", id="tasks-in-waves"),
            pytest.param("T9.99 is split into 7 tasks over 2 waves. The 7 tasks run as below.", id="the-tasks"),
            pytest.param("Wave 1 (4 tasks) writes the tests. Wave 2 has 3 tasks.", id="per-wave-counts"),
            pytest.param("The 3 tasks of wave 2 implement the code.", id="the-tasks-of-a-wave"),
            pytest.param("Eight test-writer tasks come first.", id="counts-in-words"),
        ],
    )
    def test_a_summary_that_agrees_with_the_graph_passes(self, tmp_path: Path, summary: str) -> None:
        assert self.run_with_summary(tmp_path, summary) == (0, "")

    @pytest.mark.parametrize(
        ("summary", "needle"),
        [
            pytest.param("The 9 tasks follow the layers.", "'The 9 tasks'", id="the-tasks"),
            pytest.param("The graph has 9 tasks in 2 waves.", "'9 tasks in 2 waves'", id="tasks"),
            pytest.param("The graph has 7 tasks in 3 waves.", "'in 3 waves'", id="waves"),
            pytest.param("Planned as 6 tasks across 2 waves.", "'6 tasks across 2 waves'", id="across"),
        ],
    )
    def test_a_summary_count_the_graph_does_not_hold_is_refused(
        self, tmp_path: Path, summary: str, needle: str
    ) -> None:
        code, out = self.run_with_summary(tmp_path, summary)
        assert code == 1
        assert needle in out
        assert "7 tasks" in out or "2 waves" in out

    def test_a_summary_heading_with_an_icon_is_checked_too(self, tmp_path: Path) -> None:
        code, out = self.run_with_summary(tmp_path, "The 27 tasks follow the layers.", heading="## 🧭 Summary")
        assert code == 1
        assert "'The 27 tasks'" in out
