from __future__ import annotations

# Standard library imports
from pathlib import Path
from typing import ClassVar, Dict, List, Union

# Third-party imports
import pytest
import yaml
from pydantic import JsonValue


class TestDevCellWorkflow:
    READ_ONLY_PERMISSIONS: ClassVar[Dict[str, str]] = {"contents": "read"}
    TRIGGERS: ClassVar[List[str]] = ["workflow_dispatch", "delete"]
    ACTION_OPTIONS: ClassVar[List[str]] = ["up", "down"]
    JOB_NAME: ClassVar[str] = "cell"
    SECRET_ENV: ClassVar[List[str]] = [
        "TF_BACKEND_CONFIG",
        "DEV_CELL_TFVARS",
        "DEV_CELL_KUBECONFIG",
        "AWS_ACCESS_KEY_ID",
        "AWS_SECRET_ACCESS_KEY",
    ]
    SCRIPT_COMMAND: ClassVar[str] = 'bash deploy/scripts/dev-cell.sh "$ACTION" "$BRANCH"'
    SCRIPT_ENV: ClassVar[List[str]] = ["DEV_CELL_BACKEND_CONFIG", "DEV_CELL_VAR_FILE", "KUBECONFIG"]
    FILE_SECRETS: ClassVar[List[str]] = ["TF_BACKEND_CONFIG", "DEV_CELL_TFVARS", "DEV_CELL_KUBECONFIG"]

    def workflow(self) -> Dict[Union[str, bool], JsonValue]:
        root = Path(__file__).resolve().parents[3]
        path = root / ".github" / "workflows" / "dev-cell.yml"
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert isinstance(data, dict)
        return data

    def triggers(self) -> Dict[str, JsonValue]:
        data = self.workflow()
        trigger = data.get("on", data.get(True))
        assert isinstance(trigger, dict)
        return trigger

    def jobs(self) -> Dict[str, JsonValue]:
        jobs = self.workflow()["jobs"]
        assert isinstance(jobs, dict)
        return jobs

    def job(self) -> Dict[str, JsonValue]:
        job = self.jobs()[self.JOB_NAME]
        assert isinstance(job, dict)
        return job

    def env(self) -> Dict[str, str]:
        env = self.job().get("env")
        assert isinstance(env, dict)
        return {str(key): str(value) for key, value in env.items()}

    def steps(self) -> List[Dict[str, JsonValue]]:
        steps = self.job()["steps"]
        assert isinstance(steps, list)
        return [step for step in steps if isinstance(step, dict)]

    def run_steps(self) -> List[Dict[str, JsonValue]]:
        return [step for step in self.steps() if "run" in step]

    def runs(self) -> List[str]:
        return [str(step["run"]) for step in self.run_steps()]

    def test_it_runs_on_demand_and_when_a_branch_is_deleted(self) -> None:
        assert set(self.triggers()) == set(self.TRIGGERS)

    def test_the_manual_trigger_takes_an_action_choice_and_a_branch(self) -> None:
        dispatch = self.triggers()["workflow_dispatch"]
        assert isinstance(dispatch, dict)
        inputs = dispatch["inputs"]
        assert isinstance(inputs, dict)
        action = inputs["action"]
        assert isinstance(action, dict)
        assert action["type"] == "choice"
        assert action["options"] == self.ACTION_OPTIONS
        assert action["required"] is True
        branch = inputs["branch"]
        assert isinstance(branch, dict)
        assert branch["type"] == "string"

    def test_it_only_reads_the_repository(self) -> None:
        assert self.workflow()["permissions"] == self.READ_ONLY_PERMISSIONS

    def test_cells_are_never_changed_at_the_same_time(self) -> None:
        concurrency = self.workflow()["concurrency"]
        assert isinstance(concurrency, dict)
        assert "dev-cell" in str(concurrency["group"])
        assert concurrency["cancel-in-progress"] is False

    def test_it_has_one_job_called_cell(self) -> None:
        assert set(self.jobs()) == {self.JOB_NAME}

    def test_the_deletion_of_a_tag_is_ignored(self) -> None:
        assert "github.event.ref_type == 'branch'" in str(self.job().get("if", ""))

    def test_a_deleted_branch_waits_until_the_dev_cell_is_configured(self) -> None:
        condition = str(self.job().get("if", ""))
        assert "github.event.ref_type == 'branch' && vars.DEV_CELL_MACHINES != ''" in condition
        assert "github.event_name == 'workflow_dispatch'" in condition

    def test_a_deleted_branch_destroys_its_cell(self) -> None:
        env = self.env()
        assert "delete" in env["ACTION"]
        assert "down" in env["ACTION"]
        assert "github.event.ref" in env["BRANCH"]

    @pytest.mark.parametrize("name", SECRET_ENV)
    def test_the_credentials_come_from_secrets(self, name: str) -> None:
        assert f"secrets.{name}" in self.env()[name]

    def test_it_checks_out_the_repository(self) -> None:
        uses = [str(step.get("uses", "")) for step in self.steps()]
        assert any(value.startswith("actions/checkout@") for value in uses)

    def test_terraform_is_installed_without_its_wrapper(self) -> None:
        installs = [step for step in self.steps() if str(step.get("uses", "")).startswith("hashicorp/setup-terraform@")]
        assert installs
        for step in installs:
            settings = step["with"]
            assert isinstance(settings, dict)
            assert str(settings["terraform_wrapper"]).lower() == "false"

    def test_a_step_writes_the_three_files_and_refuses_an_empty_secret(self) -> None:
        writers = [run for run in self.runs() if "RUNNER_TEMP" in run and "::error::" in run]
        assert writers
        for name in self.FILE_SECRETS:
            assert any(name in run for run in writers)

    def test_the_script_runs_with_the_files_it_needs(self) -> None:
        steps = [step for step in self.run_steps() if self.SCRIPT_COMMAND in str(step["run"])]
        assert len(steps) == 1
        env = steps[0]["env"]
        assert isinstance(env, dict)
        for name in self.SCRIPT_ENV:
            assert name in env

    def test_no_run_step_uses_an_expression(self) -> None:
        assert self.runs()
        assert all("${{" not in run for run in self.runs())
