from __future__ import annotations

from pathlib import Path
from typing import ClassVar, Dict, List, Union, cast

import yaml
from pydantic import JsonValue


class TestGitflowWorkflows:
    ROOT: ClassVar[Path] = Path(__file__).resolve().parents[3]
    WAITED_FOR: ClassVar[List[str]] = ["ci", "gitflow", "terraform", "desktop"]

    def load(self, name: str) -> Dict[Union[str, bool], JsonValue]:
        path = self.ROOT / ".github" / "workflows" / name
        return cast(Dict[Union[str, bool], JsonValue], yaml.safe_load(path.read_text(encoding="utf-8")))

    def triggers(self, name: str) -> Dict[str, Dict[str, JsonValue]]:
        data = self.load(name)
        return cast(Dict[str, Dict[str, JsonValue]], data.get("on", data.get(True)))

    def run_of(self, name: str, job: str) -> str:
        jobs = cast(Dict[str, Dict[str, JsonValue]], self.load(name)["jobs"])
        steps = cast(List[Dict[str, JsonValue]], jobs[job]["steps"])
        return " ".join(str(step.get("run", "")) for step in steps)

    def test_automerge_waits_for_every_checking_workflow(self) -> None:
        assert self.triggers("automerge.yml")["workflow_run"]["workflows"] == self.WAITED_FOR

    def test_automerge_only_merges_labelled_pull_requests_to_develop_whose_checks_passed(self) -> None:
        script = self.run_of("automerge.yml", "merge")
        assert '.name == "automerge"' in script
        assert '.baseRefName == "develop"' in script
        assert "success|skipped|neutral" in script
        assert "--match-head-commit" in script

    def test_automerge_reads_the_check_runs_of_the_head_commit_through_rest(self) -> None:
        script = self.run_of("automerge.yml", "merge")
        assert "repos/$REPO/commits/$HEAD_SHA/check-runs" in script
        assert "statusCheckRollup" not in script

    def test_automerge_may_read_the_checks_and_merge(self) -> None:
        permissions = cast(Dict[str, str], self.load("automerge.yml")["permissions"])
        assert permissions["checks"] == "read"
        assert permissions["statuses"] == "read"
        assert permissions["contents"] == "write"
        assert permissions["pull-requests"] == "write"

    def test_a_pull_request_that_changes_ci_is_left_to_a_person(self) -> None:
        script = self.run_of("automerge.yml", "merge")
        assert "repos/$REPO/pulls/$pr/files" in script
        assert ".github/workflows/" in script
        assert "needs-person" in script
        assert script.index("needs-person") < script.index("gh pr merge")

    def test_automerge_keeps_the_gitflow_merge_commit(self) -> None:
        script = self.run_of("automerge.yml", "merge")
        assert "--merge" in script
        assert "--squash" not in script
        assert "--rebase" not in script

    def test_gitflow_checks_every_pull_request(self) -> None:
        assert "pull_request" in self.triggers("gitflow.yml")

    def test_gitflow_sends_features_to_develop_and_releases_to_master(self) -> None:
        script = self.run_of("gitflow.yml", "rules")
        assert "feature/*|bugfix/*)" in script
        assert "release/*|hotfix/*)" in script

    def test_no_script_interpolates_event_values_directly(self) -> None:
        for name, job in (("gitflow.yml", "rules"), ("automerge.yml", "merge")):
            assert "${{ github.event" not in self.run_of(name, job)
