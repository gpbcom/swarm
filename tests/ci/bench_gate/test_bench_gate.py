from __future__ import annotations

# Standard library imports
import json
from pathlib import Path
from typing import ClassVar, List

# Third-party imports
import pytest

# First-party imports
from tests.ci.bench_gate.helpers import run_gate, write_change


class TestBenchGate:
    NO_BASELINE: ClassVar[str] = "No benchmark was compared with a baseline: the gate passes."

    def test_a_benchmark_six_percent_slower_fails_the_gate(self, tmp_path: Path) -> None:
        write_change(tmp_path, "safety_tick", 0.06)
        result = run_gate("--criterion-dir", str(tmp_path))
        assert result.returncode == 1
        assert result.stdout.splitlines()[0] == "safety_tick: +6.00 % regression"
        assert result.stdout.splitlines()[-1] == "Benchmark gate failed: 1 regression(s) of more than 5.00 %."

    def test_a_benchmark_slowed_down_by_a_hundred_percent_fails_the_gate(self, tmp_path: Path) -> None:
        write_change(tmp_path, "safety_tick", 1.0)
        result = run_gate("--criterion-dir", str(tmp_path))
        assert result.returncode == 1
        assert "safety_tick: +100.00 % regression" in result.stdout

    def test_exactly_five_percent_passes_because_only_more_than_five_fails(self, tmp_path: Path) -> None:
        write_change(tmp_path, "safety_tick", 0.05)
        result = run_gate("--criterion-dir", str(tmp_path))
        assert result.returncode == 0
        assert result.stdout.splitlines() == [
            "safety_tick: +5.00 % ok",
            "Benchmark gate passed: 1 benchmark(s) compared.",
        ]

    @pytest.mark.parametrize(("mean", "shown"), [(0.0, "+0.00"), (0.049, "+4.90"), (-0.2, "-20.00")])
    def test_a_change_within_the_threshold_or_an_improvement_passes(
        self, tmp_path: Path, mean: float, shown: str
    ) -> None:
        write_change(tmp_path, "planner_plan", mean)
        result = run_gate("--criterion-dir", str(tmp_path))
        assert result.returncode == 0
        assert result.stdout.splitlines()[0] == f"planner_plan: {shown} % ok"

    def test_one_regression_among_three_benchmarks_is_counted_and_lines_are_sorted(self, tmp_path: Path) -> None:
        write_change(tmp_path, "safety_tick", 0.02)
        write_change(tmp_path, "planner_plan", 0.08)
        write_change(tmp_path, "mavlink_encode", -0.01)
        result = run_gate("--criterion-dir", str(tmp_path))
        assert result.returncode == 1
        assert result.stdout.splitlines() == [
            "mavlink_encode: -1.00 % ok",
            "planner_plan: +8.00 % regression",
            "safety_tick: +2.00 % ok",
            "Benchmark gate failed: 1 regression(s) of more than 5.00 %.",
        ]

    def test_a_looser_threshold_lets_six_percent_pass(self, tmp_path: Path) -> None:
        write_change(tmp_path, "safety_tick", 0.06)
        result = run_gate("--criterion-dir", str(tmp_path), "--threshold", "0.10")
        assert result.returncode == 0
        assert result.stdout.splitlines()[0] == "safety_tick: +6.00 % ok"

    def test_no_change_file_passes_with_the_no_baseline_line(self, tmp_path: Path) -> None:
        result = run_gate("--criterion-dir", str(tmp_path))
        assert result.returncode == 0
        assert result.stdout.splitlines()[-1] == self.NO_BASELINE

    def test_the_new_estimates_are_ignored(self, tmp_path: Path) -> None:
        write_change(tmp_path, "safety_tick", 0.01)
        (tmp_path / "safety_tick" / "change" / "estimates.json").unlink()
        result = run_gate("--criterion-dir", str(tmp_path))
        assert result.returncode == 0
        assert result.stdout.splitlines() == [self.NO_BASELINE]

    @pytest.mark.parametrize(
        "args",
        [
            [],
            ["--criterion-dir", "{dir}", "--unknown"],
            ["--criterion-dir", "{dir}", "--threshold", "abc"],
            ["--criterion-dir", "{dir}", "--threshold", "-0.1"],
            ["--criterion-dir", "{dir}/missing"],
        ],
    )
    def test_bad_arguments_exit_with_two_and_a_message(self, tmp_path: Path, args: List[str]) -> None:
        result = run_gate(*[argument.replace("{dir}", str(tmp_path)) for argument in args])
        assert result.returncode == 2
        assert result.stderr.strip()

    @pytest.mark.parametrize(
        "content",
        ["{not json", json.dumps({"mean": {}}), json.dumps({"mean": {"point_estimate": "fast"}}), json.dumps({})],
    )
    def test_an_unreadable_estimates_file_exits_with_two_and_a_message(self, tmp_path: Path, content: str) -> None:
        path = tmp_path / "safety_tick" / "change" / "estimates.json"
        path.parent.mkdir(parents=True)
        path.write_text(content, encoding="utf-8")
        result = run_gate("--criterion-dir", str(tmp_path))
        assert result.returncode == 2
        assert result.stderr.strip()

    def test_a_nested_id_is_reported_with_its_full_relative_path(self, tmp_path: Path) -> None:
        write_change(tmp_path, "group/function/1000", 0.07)
        result = run_gate("--criterion-dir", str(tmp_path))
        assert result.returncode == 1
        assert result.stdout.splitlines()[0] == "group/function/1000: +7.00 % regression"
