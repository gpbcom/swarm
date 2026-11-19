from __future__ import annotations

# Standard library imports
from pathlib import Path
from typing import Dict, List, Tuple

import pytest

from tests.harness.check_plan.helpers import (
    APPROVED,
    AWAITING,
    REJECTED,
    TICKET_ID,
    json_block,
    plan_text,
    repo_root,
    run_script,
    sample_tasks,
    with_change,
    with_cycle,
    with_cycle_and_rising_waves,
    with_duplicate_id,
    with_implementer_without_test_writer,
    with_shared_file,
    without_key,
    write_plan,
    write_plan_text,
)


class TestCheckPlan:
    def run_on(self, tmp_path: Path, *args: str) -> Tuple[int, str, str]:
        result = run_script(TICKET_ID, "--root", str(tmp_path), *args)
        return result.returncode, result.stdout, result.stderr

    @pytest.mark.parametrize("status", [APPROVED, AWAITING])
    def test_the_sample_plan_passes_silently_with_either_status(self, tmp_path: Path, status: str) -> None:
        write_plan(tmp_path, status, sample_tasks())
        assert self.run_on(tmp_path) == (0, "", "")

    def test_the_sample_plan_passes_with_three_parallel_tasks_required(self, tmp_path: Path) -> None:
        write_plan(tmp_path, APPROVED, sample_tasks())
        assert self.run_on(tmp_path, "--min-parallel", "3") == (0, "", "")

    def test_a_plan_narrower_than_the_required_parallelism_is_refused(self, tmp_path: Path) -> None:
        write_plan(tmp_path, APPROVED, sample_tasks())
        code, out, _ = self.run_on(tmp_path, "--min-parallel", "9")
        assert code == 1
        assert out.startswith(f"docs/tickets/{TICKET_ID}/PLAN.md: ")
        assert "9" in out

    @pytest.mark.parametrize(
        ("tasks", "needle"),
        [
            pytest.param(without_key("id"), "id", id="missing-id"),
            pytest.param(without_key("title"), "title", id="missing-title"),
            pytest.param(without_key("agent"), "agent", id="missing-agent"),
            pytest.param(without_key("depends_on"), "depends_on", id="missing-depends-on"),
            pytest.param(without_key("files"), "files", id="missing-files"),
            pytest.param(without_key("brief"), "brief", id="missing-brief"),
            pytest.param(without_key("done_when"), "done_when", id="missing-done-when"),
            pytest.param(without_key("wave"), "wave", id="missing-wave"),
            pytest.param(with_change(0, "agent", "planner"), "planner", id="unknown-agent"),
            pytest.param(with_duplicate_id(), "K01", id="duplicate-id"),
            pytest.param(with_change(6, "id", "T1"), "T1", id="bad-id-shape"),
            pytest.param(with_change(3, "depends_on", ["K99"]), "K99", id="unknown-dependency"),
            pytest.param(with_cycle(), "K04", id="cycle"),
            pytest.param(with_cycle_and_rising_waves(), "K04", id="cycle-with-rising-waves"),
            pytest.param(with_change(3, "wave", 1), "K04", id="wave-not-after-dependency"),
            pytest.param(with_shared_file(), "src/k01.py", id="shared-file-in-one-wave"),
            pytest.param(with_change(1, "wave", 2), "K02", id="test-writer-in-wave-2"),
            pytest.param(with_implementer_without_test_writer(), "K04", id="implementer-without-test-writer"),
            pytest.param(with_change(0, "files", []), "K01", id="empty-files"),
        ],
    )
    def test_each_broken_plan_is_refused_with_a_line_naming_the_problem(
        self, tmp_path: Path, tasks: List[Dict[str, object]], needle: str
    ) -> None:
        write_plan(tmp_path, APPROVED, tasks)
        code, out, _ = self.run_on(tmp_path)
        assert code == 1
        lines = out.splitlines()
        assert lines
        assert all(line.startswith(f"docs/tickets/{TICKET_ID}/PLAN.md: ") for line in lines)
        assert needle in out

    @pytest.mark.parametrize(
        ("text", "needle"),
        [
            pytest.param(plan_text(REJECTED, json_block(sample_tasks())), "Rejected", id="bad-status"),
            pytest.param(plan_text(APPROVED, "No graph here.\n"), "json", id="no-json-block"),
            pytest.param(
                plan_text(APPROVED, json_block(sample_tasks()) + "\n" + json_block(sample_tasks())),
                "json",
                id="two-json-blocks",
            ),
            pytest.param(plan_text(APPROVED, "```json\n[{oops\n```\n"), "json", id="invalid-json"),
        ],
    )
    def test_each_broken_plan_file_is_refused(self, tmp_path: Path, text: str, needle: str) -> None:
        write_plan_text(tmp_path, text)
        code, out, _ = self.run_on(tmp_path)
        assert code == 1
        assert out.startswith(f"docs/tickets/{TICKET_ID}/PLAN.md: ")
        assert needle in out

    def test_a_missing_plan_is_refused(self, tmp_path: Path) -> None:
        code, out, _ = self.run_on(tmp_path)
        assert code == 1
        assert out.startswith(f"docs/tickets/{TICKET_ID}/PLAN.md: ")

    @pytest.mark.parametrize("ticket_id", ["T1", "X0.01", "T0.1", "T0.011", "T0.01x"])
    def test_a_bad_ticket_id_gives_usage_and_exit_2(self, tmp_path: Path, ticket_id: str) -> None:
        result = run_script(ticket_id, "--root", str(tmp_path))
        assert result.returncode == 2
        assert result.stderr.strip()
        assert result.stdout == ""

    def test_the_approved_plan_of_t0_01_passes_silently(self) -> None:
        assert (repo_root() / "docs" / "tickets" / "T0.01" / "PLAN.md").exists()
        result = run_script("T0.01", "--min-parallel", "3")
        assert (result.returncode, result.stdout, result.stderr) == (0, "", "")
