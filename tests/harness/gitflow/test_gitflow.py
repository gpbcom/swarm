from __future__ import annotations

# Standard library imports
from pathlib import Path

# Third-party imports
import pytest

# First-party imports
from tests.harness.gitflow.helpers import BYPASS_ENV, commit, git, guard, make_repo


class TestGitflowHooks:
    def test_a_commit_on_develop_is_refused(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        result = commit(main, "straight on develop")
        assert result.returncode != 0
        assert "pull request" in result.stderr

    def test_the_bypass_lets_the_person_commit_on_develop(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        assert commit(main, "a release fix", **{BYPASS_ENV: "1"}).returncode == 0

    @pytest.mark.parametrize("branch", ["feature/harness-gitflow", "release/0.1.0", "hotfix/fix-login", "bugfix/x"])
    def test_a_commit_on_a_gitflow_branch_is_accepted(self, tmp_path: Path, branch: str) -> None:
        main = make_repo(tmp_path)
        git(main, "checkout", "-b", branch)
        assert commit(main, "work").returncode == 0

    def test_a_branch_outside_gitflow_is_refused(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        git(main, "checkout", "-b", "my-stuff")
        result = commit(main, "work")
        assert result.returncode != 0
        assert "feature/" in result.stderr

    def test_a_worker_never_commits(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        git(main, "checkout", "-b", "worktree-wf_1")
        result = commit(main, "a task")
        assert result.returncode != 0
        assert "TKT-5" in result.stderr

    def test_a_ticket_commit_starts_with_its_id(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        git(main, "checkout", "-b", "feature/T0.09")
        assert commit(main, "NATS JetStream").returncode != 0
        assert commit(main, "T0.09: NATS JetStream and Operator accounts").returncode == 0

    def test_a_commit_on_the_shared_branch_starts_with_a_ticket_id(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        git(main, "checkout", "-b", "feature/tickets")
        assert commit(main, "some work").returncode != 0
        assert commit(main, "T0.10: Dev cell observability").returncode == 0

    def test_a_push_to_develop_is_refused_and_a_feature_branch_is_pushed(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        remote = tmp_path / "remote.git"
        git(tmp_path, "init", "--bare", str(remote))
        git(main, "remote", "add", "origin", str(remote))
        refused = git(main, "push", "origin", "develop")
        assert refused.returncode != 0
        assert "pull request" in refused.stderr
        git(main, "checkout", "-b", "feature/x")
        assert git(main, "push", "origin", "feature/x").returncode == 0

    def test_develop_and_master_are_never_deleted_on_github_and_a_merged_branch_is(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        remote = tmp_path / "remote.git"
        git(tmp_path, "init", "--bare", str(remote))
        git(main, "remote", "add", "origin", str(remote))
        git(main, "branch", "master")
        git(main, "branch", "feature/merged")
        assert git(main, "push", "origin", "develop", "master", "feature/merged", **{BYPASS_ENV: "1"}).returncode == 0
        for protected in ("develop", "master"):
            refused = git(main, "push", "origin", "--delete", protected)
            assert refused.returncode != 0
            assert "TKT-25" in refused.stderr
        assert git(main, "push", "origin", "--delete", "feature/merged").returncode == 0


class TestGuardHook:
    @pytest.mark.parametrize(
        "command",
        [
            "git commit -m wip",
            "git merge develop",
            "git push origin feature/T0.09",
            "git reset --hard HEAD~1",
            "git stash",
            "git rebase develop",
            "gh pr merge 12",
        ],
    )
    def test_agents_in_a_ticket_worktree_leave_git_to_ticket_tree(self, tmp_path: Path, command: str) -> None:
        main = make_repo(tmp_path)
        git(main, "checkout", "-b", "feature/T0.09")
        decision = guard(command, main)
        assert decision["permissionDecision"] == "deny"
        assert "ticket_tree.py" in str(decision["permissionDecisionReason"])

    def test_agents_on_the_shared_branch_leave_git_to_ticket_tree(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        git(main, "checkout", "-b", "feature/tickets")
        assert guard("git commit -m wip", main)["permissionDecision"] == "deny"
        assert guard("git push origin feature/tickets", main)["permissionDecision"] == "deny"

    def test_approving_a_group_of_plans_asks_the_person(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        decision = guard("python3 .claude/scripts/tickets/tickets.py approve '#12'", main)
        assert decision["permissionDecision"] == "ask"
        assert "TKT-3" in str(decision["permissionDecisionReason"])

    def test_starting_a_release_asks_the_person(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        decision = guard("gh workflow run release.yml --ref develop -f version=0.1.0", main)
        assert decision["permissionDecision"] == "ask"
        assert "TKT-26" in str(decision["permissionDecisionReason"])

    def test_a_worker_cannot_commit_either(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        git(main, "checkout", "-b", "worktree-wf_3")
        assert guard("git add -A && git commit -m x", main)["permissionDecision"] == "deny"

    @pytest.mark.parametrize(
        "command",
        [
            "git status",
            "git diff develop",
            "python3 .claude/scripts/tickets/ticket_tree.py finish --ticket T0.09",
            "git log --oneline",
        ],
    )
    def test_reading_git_and_the_harness_scripts_are_allowed(self, tmp_path: Path, command: str) -> None:
        main = make_repo(tmp_path)
        git(main, "checkout", "-b", "feature/T0.09")
        assert guard(command, main) == {}

    def test_skipping_the_hooks_is_refused_everywhere(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        assert guard("git commit --no-verify -m x", main)["permissionDecision"] == "deny"

    def test_words_in_a_message_or_a_script_are_not_options(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        git(main, "checkout", "-b", "feature/harness-gitflow")
        heredoc = "git commit -q -F - <<'EOF'\nThe hooks refuse --no-verify and git push origin develop.\nEOF"
        assert guard(heredoc, main) == {}
        assert guard('git commit -m "the hooks refuse --no-verify"', main) == {}

    def test_a_push_to_develop_from_the_main_checkout_asks_the_person(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        assert guard("git push origin develop", main)["permissionDecision"] == "ask"

    @pytest.mark.parametrize(
        ("branch", "command"),
        [
            ("master", "git rebase develop"),
            ("master", "git reset --hard origin/develop"),
            ("develop", "git rebase origin/develop"),
            ("feature/live", "git rebase develop master"),
            ("feature/live", "git push --force origin master"),
            ("feature/live", "git push -f origin develop"),
            ("feature/live", "git push origin +master"),
            ("feature/live", "git push origin --delete develop"),
        ],
    )
    def test_develop_and_master_are_never_rebased_reset_or_forced(
        self, tmp_path: Path, branch: str, command: str
    ) -> None:
        main = make_repo(tmp_path)
        git(main, "checkout", "-b", branch)
        decision = guard(command, main)
        assert decision["permissionDecision"] == "deny"
        assert "TKT-25" in str(decision["permissionDecisionReason"])

    def test_a_live_branch_is_rebased_onto_develop(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        git(main, "checkout", "-b", "feature/live")
        assert guard("git rebase origin/develop", main) == {}
        assert guard("git push --force-with-lease origin feature/live", main) == {}

    def test_the_person_s_own_git_work_in_the_main_checkout_is_left_alone(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        git(main, "checkout", "-b", "feature/harness-gitflow")
        assert guard("git commit -m 'harness: gitflow'", main) == {}
