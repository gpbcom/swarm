from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import ClassVar, Dict, List, Set, Union, cast

import pytest
import yaml
from pydantic import JsonValue


class TestCiWorkflow:
    READ_ONLY_PERMISSIONS: ClassVar[Dict[str, str]] = {"contents": "read"}
    ROOT: ClassVar[Path] = Path(__file__).resolve().parents[3]
    OUTPUT_KEYS: ClassVar[Set[str]] = {"services", "typescript", "rust", "repository", "specs"}
    JOBS: ClassVar[Set[str]] = {"changes", "python", "rust", "typescript", "specs"}

    def load(self) -> Dict[Union[str, bool], JsonValue]:
        path = self.ROOT / ".github" / "workflows" / "ci.yml"
        return cast(Dict[Union[str, bool], JsonValue], yaml.safe_load(path.read_text(encoding="utf-8")))

    def jobs(self) -> Dict[str, Dict[str, JsonValue]]:
        return cast(Dict[str, Dict[str, JsonValue]], self.load()["jobs"])

    def steps(self, job: str) -> List[Dict[str, JsonValue]]:
        return cast(List[Dict[str, JsonValue]], self.jobs()[job].get("steps", []))

    def step_using(self, job: str, action: str) -> Dict[str, JsonValue]:
        for step in self.steps(job):
            if str(step.get("uses", "")).startswith(action + "@"):
                return step
        raise AssertionError(f"No step of {job} uses {action}.")

    def all_runs(self) -> List[str]:
        runs: List[str] = []
        for job in self.jobs():
            runs.extend(str(step["run"]) for step in self.steps(job) if "run" in step)
        return runs

    def with_of(self, job: str) -> Dict[str, JsonValue]:
        return cast(Dict[str, JsonValue], self.jobs()[job].get("with", {}))

    def test_it_runs_on_push_and_pull_request(self) -> None:
        data = self.load()
        triggers = cast(Dict[str, JsonValue], data.get("on", data.get(True)))
        assert {"push", "pull_request"} <= set(triggers)

    def test_the_token_is_read_only(self) -> None:
        assert self.load()["permissions"] == self.READ_ONLY_PERMISSIONS

    def test_it_has_exactly_the_expected_jobs(self) -> None:
        assert set(self.jobs()) == self.JOBS

    def test_the_changes_job_runs_on_ubuntu_latest(self) -> None:
        assert self.jobs()["changes"]["runs-on"] == "ubuntu-latest"

    def test_the_changes_job_checks_out_the_full_history(self) -> None:
        step = self.step_using("changes", "actions/checkout")
        assert cast(Dict[str, JsonValue], step["with"])["fetch-depth"] == 0

    def test_the_changes_job_sets_up_python_3_12(self) -> None:
        step = self.step_using("changes", "actions/setup-python")
        assert str(cast(Dict[str, JsonValue], step["with"])["python-version"]) == "3.12"

    def test_the_detect_step_runs_the_detector_and_writes_the_outputs(self) -> None:
        detect = [step for step in self.steps("changes") if step.get("id") == "detect"]
        assert len(detect) == 1
        run = str(detect[0]["run"])
        assert ".github/scripts/detect_changes.py" in run
        assert "GITHUB_OUTPUT" in run

    def test_the_changes_job_outputs_come_from_the_detect_step(self) -> None:
        outputs = cast(Dict[str, str], self.jobs()["changes"]["outputs"])
        assert set(outputs) == self.OUTPUT_KEYS
        for key, value in outputs.items():
            assert value == "${{ steps.detect.outputs." + key + " }}"

    def test_the_outputs_match_the_keys_the_detector_prints(self) -> None:
        script = self.ROOT / ".github" / "scripts" / "detect_changes.py"
        result = subprocess.run(
            [sys.executable, str(script), "--all", "--root", str(self.ROOT)],
            capture_output=True,
            text=True,
            check=True,
        )
        printed = {line.split("=", 1)[0] for line in result.stdout.splitlines() if "=" in line}
        outputs = cast(Dict[str, str], self.jobs()["changes"]["outputs"])
        assert set(outputs) == printed

    @pytest.mark.parametrize("job", ["python", "rust", "typescript", "specs"])
    def test_step_two_jobs_wait_for_the_change_detection(self, job: str) -> None:
        needs = self.jobs()[job]["needs"]
        assert needs == "changes" or "changes" in cast(List[str], needs)

    @pytest.mark.parametrize(
        ("job", "workflow", "conditions"),
        [
            ("python", "python.yml", ["needs.changes.outputs.services", "needs.changes.outputs.repository"]),
            ("rust", "rust.yml", ["needs.changes.outputs.rust"]),
            ("typescript", "typescript.yml", ["needs.changes.outputs.typescript"]),
            ("specs", "specs.yml", ["needs.changes.outputs.specs"]),
        ],
    )
    def test_each_language_job_calls_its_workflow_under_its_condition(
        self, job: str, workflow: str, conditions: List[str]
    ) -> None:
        assert self.jobs()[job]["uses"] == f"./.github/workflows/{workflow}"
        for condition in conditions:
            assert condition in str(self.jobs()[job]["if"])

    def test_the_python_job_receives_the_services_and_the_repository_flag(self) -> None:
        inputs = self.with_of("python")
        assert inputs["services"] == "${{ needs.changes.outputs.services }}"
        assert "needs.changes.outputs.repository" in str(inputs["repository"])

    def test_the_typescript_job_receives_the_projects(self) -> None:
        assert self.with_of("typescript")["projects"] == "${{ needs.changes.outputs.typescript }}"

    def test_no_script_interpolates_event_values_directly(self) -> None:
        for run in self.all_runs():
            assert "${{ github.event" not in run

    @pytest.mark.parametrize("word", ["docker", "cosign", "trivy", "playwright"])
    def test_steps_three_to_six_are_not_built_yet(self, word: str) -> None:
        for run in self.all_runs():
            assert word not in run.lower()

    def test_no_step_uses_a_docker_action(self) -> None:
        for job in self.jobs():
            for step in self.steps(job):
                assert not str(step.get("uses", "")).startswith("docker/")
