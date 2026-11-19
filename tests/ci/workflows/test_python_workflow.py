from __future__ import annotations

from pathlib import Path
from typing import ClassVar, Dict, List, Union

import pytest
import yaml
from pydantic import JsonValue


class TestPythonWorkflow:
    READ_ONLY_PERMISSIONS: ClassVar[Dict[str, str]] = {"contents": "read"}

    def root(self) -> Path:
        return Path(__file__).resolve().parents[3]

    def load(self) -> Dict[Union[str, bool], JsonValue]:
        path = self.root() / ".github" / "workflows" / "python.yml"
        assert path.is_file(), ".github/workflows/python.yml is missing."
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert isinstance(data, dict)
        return data

    def trigger(self) -> Dict[str, Dict[str, Dict[str, Dict[str, JsonValue]]]]:
        data = self.load()
        trigger = data.get("on", data.get(True))
        assert isinstance(trigger, dict)
        return trigger

    def jobs(self) -> Dict[str, Dict[str, JsonValue]]:
        jobs = self.load().get("jobs")
        assert isinstance(jobs, dict)
        return jobs

    def job(self, name: str) -> Dict[str, JsonValue]:
        return self.jobs()[name]

    def steps(self, name: str) -> List[Dict[str, JsonValue]]:
        steps = self.job(name).get("steps")
        assert isinstance(steps, list)
        return steps

    def runs(self, name: str) -> List[str]:
        return [str(step["run"]) for step in self.steps(name) if "run" in step]

    def uses(self, name: str) -> List[str]:
        return [str(step["uses"]) for step in self.steps(name) if "uses" in step]

    def run_index(self, name: str, fragment: str) -> int:
        for index, run in enumerate(self.runs(name)):
            if fragment in run:
                return index
        raise AssertionError(f"No run of job {name} contains {fragment!r}.")

    def run_with(self, name: str, fragment: str) -> str:
        return self.runs(name)[self.run_index(name, fragment)]

    def test_it_is_a_reusable_workflow_only(self) -> None:
        assert list(self.trigger()) == ["workflow_call"]

    def test_the_services_input_is_a_required_string(self) -> None:
        services = self.trigger()["workflow_call"]["inputs"]["services"]
        assert services["type"] == "string"
        assert services["required"] is True

    def test_the_repository_input_is_an_optional_boolean_off_by_default(self) -> None:
        repository = self.trigger()["workflow_call"]["inputs"]["repository"]
        assert repository["type"] == "boolean"
        assert repository["required"] is False
        assert repository["default"] is False

    def test_permissions_are_read_only(self) -> None:
        assert self.load().get("permissions") == self.READ_ONLY_PERMISSIONS

    def test_there_are_exactly_three_jobs(self) -> None:
        assert sorted(self.jobs()) == ["packages", "repository", "services"]

    @pytest.mark.parametrize("name", ["services", "repository", "packages"])
    def test_each_job_runs_on_ubuntu(self, name: str) -> None:
        assert self.job(name)["runs-on"] == "ubuntu-latest"

    def test_the_services_job_is_skipped_for_an_empty_list(self) -> None:
        condition = str(self.job("services")["if"])
        assert "inputs.services" in condition
        assert "'[]'" in condition

    def test_the_services_job_runs_one_matrix_entry_per_service(self) -> None:
        strategy = self.job("services")["strategy"]
        assert isinstance(strategy, dict)
        assert strategy["fail-fast"] is False
        assert strategy["matrix"]["service"] == "${{ fromJSON(inputs.services) }}"

    def test_the_service_name_reaches_the_shell_through_env(self) -> None:
        env = self.job("services")["env"]
        assert isinstance(env, dict)
        assert env["SERVICE"] == "${{ matrix.service }}"

    def test_the_services_job_checks_out_then_sets_up_uv_then_syncs(self) -> None:
        uses = self.uses("services")
        assert uses[0].startswith("actions/checkout@")
        assert uses[1].startswith("astral-sh/setup-uv@")
        assert self.run_index("services", "uv sync --locked") == 0

    def test_the_services_job_runs_the_four_tools_in_order(self) -> None:
        indexes = [
            self.run_index("services", command)
            for command in ["uv run ruff check", "uv run ruff format --check", "uv run mypy", "uv run pytest"]
        ]
        assert indexes == sorted(indexes)
        assert len(set(indexes)) == 4

    @pytest.mark.parametrize(
        "command, path",
        [
            ("uv run ruff check", "services/$SERVICE"),
            ("uv run ruff format --check", "services/$SERVICE"),
            ("uv run mypy", "services/$SERVICE/src"),
            ("uv run pytest", "services/$SERVICE/tests"),
        ],
    )
    def test_each_tool_targets_the_service_folder(self, command: str, path: str) -> None:
        assert path in self.run_with("services", command)

    def test_the_services_job_runs_only_its_slice_of_the_convention_tests(self) -> None:
        run = self.run_with("services", "tests/conventions/services/test_service_conventions.py")
        assert "-k" in run
        assert "$SERVICE" in run

    def test_the_services_job_never_expands_an_expression_inside_a_run(self) -> None:
        assert all("${{" not in run for run in self.runs("services"))

    def test_the_repository_job_depends_on_its_input(self) -> None:
        assert "inputs.repository" in str(self.job("repository")["if"])

    def test_the_repository_job_checks_out_then_sets_up_uv_then_syncs(self) -> None:
        uses = self.uses("repository")
        assert uses[0].startswith("actions/checkout@")
        assert uses[1].startswith("astral-sh/setup-uv@")
        assert self.run_index("repository", "uv sync --locked") == 0

    @pytest.mark.parametrize("command", ["uv run ruff check", "uv run ruff format --check"])
    def test_the_repository_job_lints_the_tests_and_the_ci_scripts(self, command: str) -> None:
        run = self.run_with("repository", command)
        assert "tests" in run
        assert ".github/scripts" in run

    def test_the_repository_job_runs_the_repository_tests_on_two_workers(self) -> None:
        run = self.run_with("repository", "uv run pytest")
        assert "tests" in run
        assert "-n 2" in run

    def test_the_packages_job_depends_on_the_repository_input(self) -> None:
        assert "inputs.repository" in str(self.job("packages")["if"])

    def test_the_packages_job_checks_out_then_sets_up_uv_then_syncs(self) -> None:
        uses = self.uses("packages")
        assert uses[0].startswith("actions/checkout@")
        assert uses[1].startswith("astral-sh/setup-uv@")
        assert self.run_index("packages", "uv sync --locked") == 0

    def test_the_packages_job_runs_its_checks_in_order(self) -> None:
        commands = [
            "uv run ruff check",
            "uv run ruff format --check",
            "uv run mypy",
            "uv run pytest",
            "uv run swarm-models-schemas --check",
        ]
        indexes = [self.run_index("packages", command) for command in commands]
        assert indexes == sorted(indexes)
        assert len(set(indexes)) == len(commands)

    @pytest.mark.parametrize(
        "command",
        ["uv run ruff check", "uv run ruff format --check", "uv run mypy", "uv run pytest"],
    )
    def test_each_packages_tool_targets_the_python_packages(self, command: str) -> None:
        assert "packages/python" in self.run_with("packages", command)

    def test_the_packages_job_runs_the_tests_on_two_workers(self) -> None:
        assert "-n 2" in self.run_with("packages", "uv run pytest")

    def test_the_packages_job_never_expands_an_expression_inside_a_run(self) -> None:
        assert all("${{" not in run for run in self.runs("packages"))
