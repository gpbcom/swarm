from __future__ import annotations

from pathlib import Path
from typing import ClassVar, Dict

from tests.ci.release.helpers import (
    GITHUB_TOKEN,
    HEAD_SHA,
    MERGE_SHA,
    RELEASE_TOKEN,
    argv,
    calls_to,
    run_automerge,
    scenario,
)


class TestAutomerge:
    GREEN: ClassVar[Dict[str, str]] = {"result": "success", "rules": "success", "rust": "skipped"}

    def test_a_release_is_merged_into_master_tagged_released_and_brought_back_to_develop(self, tmp_path: Path) -> None:
        calls = run_automerge(tmp_path, scenario("release/0.1.0", "master", [".github/workflows/ci.yml"], self.GREEN))
        [merge] = calls_to(calls, "pr", "merge")
        assert merge["token"] == RELEASE_TOKEN
        assert "Release v0.1.0: merge release/0.1.0 into master (#12)" in argv(merge)
        assert f"--match-head-commit {HEAD_SHA}" in argv(merge)
        [release] = calls_to(calls, "release", "create")
        assert argv(release).startswith(f"release create v0.1.0 -R gpbcom/swarm --target {MERGE_SHA}")
        assert release["token"] == RELEASE_TOKEN
        [back] = calls_to(calls, "pr", "create")
        assert "--base develop --head release/0.1.0 --label automerge" in argv(back)
        assert back["token"] == RELEASE_TOKEN
        assert calls.index(merge) < calls.index(release) < calls.index(back)
        assert not [call for call in calls if "DELETE" in argv(call)]

    def test_a_release_branch_deleted_by_github_on_merge_is_recreated_for_the_way_back(self, tmp_path: Path) -> None:
        case = scenario("release/0.1.0", "master", [], self.GREEN)
        case["branch_gone"] = True
        calls = run_automerge(tmp_path, case)
        [recreate] = [call for call in calls if "git/refs" in argv(call) and "POST" in argv(call)]
        assert f"ref=refs/heads/release/0.1.0 -f sha={HEAD_SHA}" in argv(recreate)
        assert recreate["token"] == RELEASE_TOKEN
        [back] = calls_to(calls, "pr", "create")
        assert calls.index(recreate) < calls.index(back)

    def test_a_release_branch_still_there_is_left_as_it_is(self, tmp_path: Path) -> None:
        calls = run_automerge(tmp_path, scenario("release/0.1.0", "master", [], self.GREEN))
        assert not [call for call in calls if "git/refs" in argv(call) and "POST" in argv(call)]

    def test_no_release_reaches_master_without_the_release_token(self, tmp_path: Path) -> None:
        calls = run_automerge(tmp_path, scenario("release/0.1.0", "master", [], self.GREEN), release_token="")
        assert not calls_to(calls, "pr", "merge")
        assert any("needs-person" in argv(call) for call in calls)
        assert any("RELEASE_TOKEN is missing" in argv(call) for call in calls)

    def test_only_a_release_or_a_hotfix_goes_to_master(self, tmp_path: Path) -> None:
        calls = run_automerge(tmp_path, scenario("feature/x", "master", [], self.GREEN))
        assert not calls_to(calls, "pr", "merge")

    def test_a_red_check_holds_the_release(self, tmp_path: Path) -> None:
        checks = {**self.GREEN, "python / repository": "failure"}
        calls = run_automerge(tmp_path, scenario("release/0.1.0", "master", [], checks))
        assert not calls_to(calls, "pr", "merge")

    def test_a_ticket_is_merged_into_develop_and_its_branch_deleted(self, tmp_path: Path) -> None:
        calls = run_automerge(tmp_path, scenario("feature/tickets", "develop", ["services/x.py"], self.GREEN))
        [merge] = calls_to(calls, "pr", "merge")
        assert merge["token"] == GITHUB_TOKEN
        assert "T0.10: merge feature/tickets into develop (#12)" in argv(merge)
        [delete] = [call for call in calls if "DELETE" in argv(call)]
        assert argv(delete).endswith("repos/gpbcom/swarm/git/refs/heads/feature/tickets --silent")
        assert calls.index(merge) < calls.index(delete)

    def test_a_branch_that_moved_after_the_merge_is_kept(self, tmp_path: Path) -> None:
        case = scenario("feature/tickets", "develop", ["services/x.py"], self.GREEN, ref_sha="c" * 40)
        calls = run_automerge(tmp_path, case)
        assert calls_to(calls, "pr", "merge")
        assert not [call for call in calls if "DELETE" in argv(call)]

    def test_the_way_back_of_a_release_is_merged_into_develop_then_its_branch_deleted(self, tmp_path: Path) -> None:
        case = scenario(
            "release/0.1.0", "develop", ["CHANGELOG.md"], self.GREEN, title="Release v0.1.0: back to develop"
        )
        calls = run_automerge(tmp_path, case)
        [merge] = calls_to(calls, "pr", "merge")
        assert merge["token"] == RELEASE_TOKEN
        assert "Release v0.1.0: merge release/0.1.0 into develop (#12)" in argv(merge)
        assert [call for call in calls if "DELETE" in argv(call)]

    def test_a_change_to_ci_bound_for_develop_is_left_to_a_person(self, tmp_path: Path) -> None:
        calls = run_automerge(tmp_path, scenario("feature/ci", "develop", [".github/workflows/ci.yml"], self.GREEN))
        assert not calls_to(calls, "pr", "merge")
        assert any("needs-person" in argv(call) for call in calls)

    def test_no_pull_request_at_this_commit_does_nothing(self, tmp_path: Path) -> None:
        case = scenario("feature/x", "develop", [], self.GREEN)
        case["prs"] = []
        calls = run_automerge(tmp_path, case)
        assert not calls_to(calls, "pr", "merge")
