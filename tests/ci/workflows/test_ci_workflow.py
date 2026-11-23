from __future__ import annotations

# Standard library imports
import subprocess
import sys
from pathlib import Path
from typing import ClassVar, Dict, List, Set, Union, cast

# Third-party imports
import pytest
import yaml
from pydantic import JsonValue


class TestCiWorkflow:
    READ_ONLY_PERMISSIONS: ClassVar[Dict[str, str]] = {"contents": "read"}
    ROOT: ClassVar[Path] = Path(__file__).resolve().parents[3]
    OUTPUT_KEYS: ClassVar[Set[str]] = {"services", "typescript", "rust", "repository", "specs", "images"}
    JOBS: ClassVar[Set[str]] = {"changes", "python", "rust", "typescript", "specs", "images", "result"}
    GITFLOW_PUSH_BRANCHES: ClassVar[List[str]] = ["master", "develop", "release/**", "hotfix/**"]
    PULL_REQUEST_BASES: ClassVar[List[str]] = ["develop", "master", "release/**"]
    CHECK_JOBS: ClassVar[Set[str]] = {"changes", "python", "rust", "typescript", "specs"}
    RESULT_NEEDS: ClassVar[Set[str]] = CHECK_JOBS | {"images"}
    IMAGES_PERMISSIONS: ClassVar[Dict[str, str]] = {"contents": "read", "packages": "write", "id-token": "write"}
    IMAGES_CONDITIONS: ClassVar[List[str]] = [
        "!cancelled()",
        "!contains(needs.*.result, 'failure')",
        "needs.changes.outputs.images != '[]'",
    ]
    PUBLISH_CONDITIONS: ClassVar[List[str]] = ["github.event_name == 'push'", "refs/heads/develop", "refs/heads/master"]

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

    def triggers(self) -> Dict[str, Dict[str, JsonValue]]:
        data = self.load()
        return cast(Dict[str, Dict[str, JsonValue]], data.get("on", data.get(True)))

    def test_pushes_run_only_on_the_gitflow_branches(self) -> None:
        assert self.triggers()["push"]["branches"] == self.GITFLOW_PUSH_BRANCHES

    def test_pull_requests_run_against_the_gitflow_bases(self) -> None:
        assert self.triggers()["pull_request"]["branches"] == self.PULL_REQUEST_BASES

    def test_a_newer_pull_request_run_cancels_the_older_one(self) -> None:
        concurrency = cast(Dict[str, JsonValue], self.load()["concurrency"])
        assert "github.ref" in str(concurrency["group"])
        assert "github.event_name == 'pull_request'" in str(concurrency["cancel-in-progress"])

    def test_the_result_job_waits_for_every_check(self) -> None:
        result = self.jobs()["result"]
        assert set(cast(List[str], result["needs"])) == self.RESULT_NEEDS
        assert "always()" in str(result["if"])

    def test_the_result_job_fails_when_a_check_failed_or_was_cancelled(self) -> None:
        run = " ".join(str(step["run"]) for step in self.steps("result") if "run" in step)
        assert "failure" in run
        assert "cancelled" in run
        assert "exit 1" in run

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

    def test_the_images_job_calls_the_images_workflow(self) -> None:
        assert self.jobs()["images"]["uses"] == "./.github/workflows/images.yml"

    def test_the_images_job_waits_for_every_check(self) -> None:
        needs = self.jobs()["images"]["needs"]
        assert set(cast(List[str], needs)) >= self.CHECK_JOBS

    def test_the_images_job_runs_only_when_no_check_failed_and_images_changed(self) -> None:
        condition = str(self.jobs()["images"]["if"]).replace(" ", "")
        for expected in self.IMAGES_CONDITIONS:
            assert expected.replace(" ", "") in condition

    def test_the_images_job_receives_the_images_to_build(self) -> None:
        assert self.with_of("images")["images"] == "${{ needs.changes.outputs.images }}"

    def test_images_are_published_from_develop_and_master_pushes_only(self) -> None:
        publish = str(self.with_of("images")["publish"])
        for expected in self.PUBLISH_CONDITIONS:
            assert expected in publish

    def test_the_images_job_may_write_packages_and_sign(self) -> None:
        assert self.jobs()["images"]["permissions"] == self.IMAGES_PERMISSIONS

    def test_no_step_uses_a_docker_action(self) -> None:
        for job in self.jobs():
            for step in self.steps(job):
                assert not str(step.get("uses", "")).startswith("docker/")
