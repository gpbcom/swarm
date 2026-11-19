from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Union

import pytest
import yaml
from pydantic import JsonValue


class TestSpecsWorkflow:
    CHECK_COMMAND = "uv run python .claude/skills/write-specs/scripts/specs.py check"

    def workflow(self) -> Dict[Union[str, bool], JsonValue]:
        root = Path(__file__).resolve().parents[3]
        with open(root / ".github" / "workflows" / "specs.yml", encoding="utf-8") as handle:
            data = yaml.safe_load(handle)
        assert isinstance(data, dict)
        return data

    def steps(self) -> List[Dict[str, JsonValue]]:
        jobs = self.workflow()["jobs"]
        assert isinstance(jobs, dict)
        steps = jobs["check"]["steps"]
        assert isinstance(steps, list)
        return steps

    def runs(self) -> List[str]:
        return [str(step["run"]) for step in self.steps() if "run" in step]

    def test_it_is_a_reusable_workflow(self) -> None:
        data = self.workflow()
        trigger = data.get("on", data.get(True))
        assert isinstance(trigger, dict)
        assert "workflow_call" in trigger

    def test_it_only_reads_the_repository(self) -> None:
        assert self.workflow()["permissions"] == {"contents": "read"}

    def test_it_has_one_check_job_on_ubuntu(self) -> None:
        jobs = self.workflow()["jobs"]
        assert isinstance(jobs, dict)
        assert list(jobs) == ["check"]
        assert jobs["check"]["runs-on"] == "ubuntu-latest"

    def test_its_steps_come_in_order(self) -> None:
        steps = self.steps()
        assert len(steps) >= 4
        assert str(steps[0].get("uses", "")).startswith("actions/checkout@")
        assert str(steps[1].get("uses", "")).startswith("astral-sh/setup-uv@")
        assert "uv sync --locked" in str(steps[2].get("run", ""))
        assert self.CHECK_COMMAND in str(steps[3].get("run", ""))

    @pytest.mark.parametrize("forbidden", ["specs.py build", "specs.py render"])
    def test_it_checks_and_never_writes(self, forbidden: str) -> None:
        assert all(forbidden not in run for run in self.runs())

    def test_no_run_uses_an_expression(self) -> None:
        assert all("${{" not in run for run in self.runs())
