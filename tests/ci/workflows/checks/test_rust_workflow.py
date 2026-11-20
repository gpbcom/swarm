from __future__ import annotations

from pathlib import Path
from typing import ClassVar, Dict, List, Optional, Union

import pytest
import yaml
from pydantic import JsonValue


class TestRustWorkflow:
    READ_ONLY_PERMISSIONS: ClassVar[Dict[str, str]] = {"contents": "read"}

    def workflow(self) -> Dict[Union[str, bool], JsonValue]:
        root = Path(__file__).resolve().parents[4]
        path = root / ".github" / "workflows" / "rust.yml"
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert isinstance(data, dict)
        return data

    def job(self) -> Dict[str, JsonValue]:
        jobs = self.workflow()["jobs"]
        assert isinstance(jobs, dict)
        return jobs["check"]

    def steps(self) -> List[Dict[str, JsonValue]]:
        return list(self.job()["steps"])

    def runs(self) -> List[str]:
        return [str(step["run"]) for step in self.steps() if "run" in step]

    def index_of(self, needle: str) -> Optional[int]:
        for index, step in enumerate(self.steps()):
            if needle in str(step.get("run", "")):
                return index
        return None

    def bench_job(self) -> Dict[str, JsonValue]:
        jobs = self.workflow()["jobs"]
        assert isinstance(jobs, dict)
        assert "bench" in jobs
        return jobs["bench"]

    def bench_steps(self) -> List[Dict[str, JsonValue]]:
        return list(self.bench_job()["steps"])

    def bench_runs(self) -> List[str]:
        return [str(step["run"]) for step in self.bench_steps() if "run" in step]

    def bench_env(self) -> Dict[str, str]:
        env: Dict[str, str] = {}
        sources = [self.bench_job().get("env")] + [step.get("env") for step in self.bench_steps()]
        for source in sources:
            if isinstance(source, dict):
                env.update({str(key): str(value) for key, value in source.items()})
        return env

    def bench_index_of(self, needle: str, after: int = -1) -> Optional[int]:
        for index, step in enumerate(self.bench_steps()):
            if index > after and needle in str(step.get("run", "")):
                return index
        return None

    def test_it_is_a_reusable_workflow(self) -> None:
        data = self.workflow()
        trigger = data.get("on", data.get(True))
        assert isinstance(trigger, dict)
        assert "workflow_call" in trigger

    def test_it_only_reads_the_repository(self) -> None:
        assert self.workflow()["permissions"] == self.READ_ONLY_PERMISSIONS

    def test_it_has_a_check_job_and_a_bench_job_on_ubuntu(self) -> None:
        jobs = self.workflow()["jobs"]
        assert isinstance(jobs, dict)
        assert set(jobs) == {"check", "bench"}
        assert self.job()["runs-on"] == "ubuntu-latest"
        assert self.bench_job()["runs-on"] == "ubuntu-latest"

    def test_it_runs_in_the_rust_workspace(self) -> None:
        assert self.job()["defaults"]["run"]["working-directory"] == "packages/rust"

    def test_it_checks_out_the_repository(self) -> None:
        uses = [str(step.get("uses", "")) for step in self.steps()]
        assert any(value.startswith("actions/checkout@") for value in uses)

    def test_the_toolchain_is_installed_before_the_first_cargo_command(self) -> None:
        first_cargo = self.index_of("cargo ")
        assert first_cargo is not None
        installs = [
            index
            for index, step in enumerate(self.steps())
            if "rust-toolchain" in str(step.get("uses", "")) or "rustup" in str(step.get("run", ""))
        ]
        assert installs
        assert min(installs) < first_cargo

    @pytest.mark.parametrize(
        "command",
        [
            "cargo fmt --all --check",
            "cargo clippy --workspace --all-targets --locked -- -D warnings",
            "cargo test --workspace --locked",
        ],
    )
    def test_it_runs_each_cargo_command(self, command: str) -> None:
        assert any(command in run for run in self.runs())

    def test_the_cargo_commands_run_in_order(self) -> None:
        positions = [
            self.index_of("cargo fmt --all --check"),
            self.index_of("cargo clippy --workspace --all-targets --locked -- -D warnings"),
            self.index_of("cargo test --workspace --locked"),
        ]
        found = [position for position in positions if position is not None]
        assert len(found) == len(positions)
        assert found == sorted(found)

    def test_no_run_step_uses_an_expression(self) -> None:
        assert all("${{" not in run for run in self.runs() + self.bench_runs())

    def test_the_bench_job_waits_for_the_check_job(self) -> None:
        needs = self.bench_job().get("needs")
        assert needs == "check" or (isinstance(needs, list) and "check" in needs)

    def test_the_bench_job_only_runs_on_pull_requests(self) -> None:
        assert "github.event_name == 'pull_request'" in str(self.bench_job().get("if", ""))

    def test_the_bench_job_runs_in_the_rust_workspace(self) -> None:
        assert self.bench_job()["defaults"]["run"]["working-directory"] == "packages/rust"

    def test_the_bench_job_checks_out_the_full_history(self) -> None:
        checkouts = [step for step in self.bench_steps() if str(step.get("uses", "")).startswith("actions/checkout@")]
        assert checkouts
        assert any(str(step.get("with", {}).get("fetch-depth")) == "0" for step in checkouts)

    def test_the_bench_toolchain_is_installed_before_the_first_cargo_command(self) -> None:
        first_cargo = self.bench_index_of("cargo ")
        assert first_cargo is not None
        installs = [
            index
            for index, step in enumerate(self.bench_steps())
            if "rust-toolchain" in str(step.get("uses", "")) or "rustup" in str(step.get("run", ""))
        ]
        assert installs
        assert min(installs) < first_cargo

    def test_the_bench_job_knows_the_base_commit(self) -> None:
        assert self.bench_env().get("BASE_SHA") == "${{ github.event.pull_request.base.sha }}"

    def test_both_benchmark_runs_share_one_criterion_folder(self) -> None:
        assert "CARGO_TARGET_DIR" in self.bench_env()

    def test_the_bench_job_saves_the_base_baseline_from_a_worktree(self) -> None:
        assert any("git worktree add" in run and "--save-baseline pr-base" in run for run in self.bench_runs())

    def test_the_bench_job_compares_the_pull_request_to_the_baseline(self) -> None:
        compare = self.bench_index_of("cargo bench --workspace --locked")
        assert compare is not None
        assert "--baseline-lenient pr-base" in str(self.bench_steps()[compare]["run"])

    def test_the_bench_job_runs_the_gate_on_the_criterion_folder(self) -> None:
        gate = self.bench_index_of(".github/scripts/bench_gate.py")
        assert gate is not None
        assert "--criterion-dir" in str(self.bench_steps()[gate]["run"])

    def test_the_bench_steps_run_in_order(self) -> None:
        save = self.bench_index_of("git worktree add")
        assert save is not None
        compare = self.bench_index_of("--baseline-lenient pr-base", after=save)
        assert compare is not None
        gate = self.bench_index_of(".github/scripts/bench_gate.py", after=compare)
        assert gate is not None
