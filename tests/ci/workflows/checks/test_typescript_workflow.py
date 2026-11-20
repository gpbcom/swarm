from __future__ import annotations

from pathlib import Path
from typing import ClassVar, Dict, List, Union

import pytest
import yaml
from pydantic import JsonValue


class TestTypescriptWorkflow:
    READ_ONLY_PERMISSIONS: ClassVar[Dict[str, str]] = {"contents": "read"}

    def workflow(self) -> Dict[Union[str, bool], JsonValue]:
        root = Path(__file__).resolve().parents[4]
        text = (root / ".github" / "workflows" / "typescript.yml").read_text(encoding="utf-8")
        data = yaml.safe_load(text)
        assert isinstance(data, dict)
        return data

    def trigger(self) -> Dict[str, JsonValue]:
        data = self.workflow()
        trigger = data.get("on", data.get(True))
        assert isinstance(trigger, dict)
        return trigger

    def check_job(self) -> Dict[str, JsonValue]:
        jobs = self.workflow()["jobs"]
        assert isinstance(jobs, dict)
        job = jobs["check"]
        assert isinstance(job, dict)
        return job

    def steps(self) -> List[Dict[str, JsonValue]]:
        steps = self.check_job()["steps"]
        assert isinstance(steps, list)
        return steps

    def runs(self) -> List[str]:
        return [str(step["run"]) for step in self.steps() if "run" in step]

    def test_it_is_a_reusable_workflow_only(self) -> None:
        assert list(self.trigger().keys()) == ["workflow_call"]

    def test_the_projects_input_is_a_required_string(self) -> None:
        call = self.trigger()["workflow_call"]
        assert isinstance(call, dict)
        projects = call["inputs"]["projects"]
        assert projects["type"] == "string"
        assert projects["required"] is True

    def test_permissions_are_read_only(self) -> None:
        assert self.workflow()["permissions"] == self.READ_ONLY_PERMISSIONS

    def test_the_only_job_is_check_on_ubuntu(self) -> None:
        jobs = self.workflow()["jobs"]
        assert isinstance(jobs, dict)
        assert list(jobs.keys()) == ["check"]
        assert self.check_job()["runs-on"] == "ubuntu-latest"

    @pytest.mark.parametrize("needle", ["inputs.projects", "'[]'"])
    def test_the_job_is_skipped_without_projects(self, needle: str) -> None:
        assert needle in str(self.check_job()["if"])

    def test_the_matrix_runs_every_project_without_failing_fast(self) -> None:
        strategy = self.check_job()["strategy"]
        assert isinstance(strategy, dict)
        assert strategy["fail-fast"] is False
        assert strategy["matrix"]["project"] == "${{ fromJSON(inputs.projects) }}"

    def test_the_project_is_exposed_as_an_environment_variable(self) -> None:
        env = self.check_job()["env"]
        assert isinstance(env, dict)
        assert env["PROJECT"] == "${{ matrix.project }}"

    def test_the_setup_steps_come_first_in_order(self) -> None:
        uses = [str(step.get("uses", "")) for step in self.steps()[:3]]
        prefixes = ["actions/checkout@", "pnpm/action-setup@", "actions/setup-node@"]
        for used, prefix in zip(uses, prefixes):
            assert used.startswith(prefix)

    def test_node_22_is_set_up_with_the_pnpm_cache(self) -> None:
        options = self.steps()[2]["with"]
        assert isinstance(options, dict)
        assert str(options["node-version"]).startswith("22")
        assert options["cache"] == "pnpm"

    def test_dependencies_are_installed_from_the_frozen_lockfile(self) -> None:
        assert "pnpm install --frozen-lockfile" in self.runs()[0]

    @pytest.mark.parametrize(("index", "script"), [(1, "lint"), (2, "typecheck"), (3, "test")])
    def test_each_script_runs_for_the_selected_project(self, index: int, script: str) -> None:
        run = self.runs()[index]
        assert "pnpm --filter" in run
        assert "$PROJECT" in run
        assert "--if-present" in run
        assert f"run --if-present {script}" in run

    def test_there_are_exactly_four_run_steps(self) -> None:
        assert len(self.runs()) == 4

    def test_no_run_step_interpolates_an_expression(self) -> None:
        for run in self.runs():
            assert "${{" not in run
