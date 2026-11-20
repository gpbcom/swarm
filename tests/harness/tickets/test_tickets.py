from __future__ import annotations

from pathlib import Path

from tests.harness.tickets.helpers import (
    DONE,
    FIELD,
    NEXT,
    OTHER_AREA,
    SAME_AREA,
    SHARED_BRANCH,
    git,
    legacy_ticket,
    lines,
    make_repo,
    open_ticket,
    run,
)


class TestTickets:
    def test_a_ticket_whose_prerequisites_are_merged_may_start(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        result = run(main, "check", "--ticket", NEXT)
        assert result.returncode == 0, result.stdout
        assert result.stdout == ""

    def test_a_ticket_with_an_open_prerequisite_waits(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        result = run(main, "check", "--ticket", OTHER_AREA)
        assert result.returncode == 1
        assert NEXT in result.stdout
        assert "not done" in result.stdout

    def test_a_prerequisite_committed_on_the_shared_branch_counts_as_done(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        git(main, "checkout", "-b", SHARED_BRANCH)
        (main / "docs" / "tickets" / NEXT).mkdir(parents=True)
        (main / "docs" / "tickets" / NEXT / "EXPLAIN.md").write_text("# Explain\n", encoding="utf-8")
        git(main, "add", "-A")
        git(main, "commit", "-m", f"{NEXT}: finished, pull request open")
        assert run(main, "check", "--ticket", OTHER_AREA).returncode == 0

    def test_a_ticket_waits_while_an_open_ticket_changes_the_same_area(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        open_ticket(main, NEXT)
        result = run(main, "check", "--ticket", SAME_AREA)
        assert result.returncode == 1
        assert "services/missions" in result.stdout
        assert NEXT in result.stdout

    def test_a_ticket_does_not_wait_for_itself(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        open_ticket(main, NEXT)
        assert run(main, "check", "--ticket", NEXT).returncode == 0

    def test_a_ticket_still_in_its_own_worktree_locks_its_areas_too(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        legacy_ticket(main, NEXT)
        assert run(main, "check", "--ticket", SAME_AREA).returncode == 1

    def test_a_field_ticket_waits_for_its_campaign(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        result = run(main, "check", "--ticket", FIELD)
        assert result.returncode == 1
        assert "C-01" in result.stdout

    def test_force_reports_the_problems_but_lets_the_ticket_start(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        result = run(main, "check", "--ticket", OTHER_AREA, "--force")
        assert result.returncode == 0
        assert NEXT in result.stdout

    def test_list_shows_every_open_ticket_and_the_files_it_owns(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        open_ticket(main, NEXT, ["src/a.py", "src/b.py", f"docs/tickets/{NEXT}/"])
        open_ticket(main, OTHER_AREA)
        shown = "\n".join(lines(run(main, "list")))
        assert NEXT in shown
        assert "3 files" in shown
        assert OTHER_AREA in shown
        assert DONE not in shown

    def test_prune_removes_a_merged_legacy_worktree_and_the_empty_folder(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        home = legacy_ticket(main, NEXT)
        (home / "docs" / "tickets" / NEXT).mkdir(parents=True)
        (home / "docs" / "tickets" / NEXT / "EXPLAIN.md").write_text("# Explain\n", encoding="utf-8")
        git(home, "add", "-A")
        git(home, "commit", "-m", f"{NEXT}: work")
        git(main, "merge", "--no-ff", f"feature/{NEXT}", "-m", "merge")
        result = run(main, "prune")
        assert result.returncode == 0, result.stderr
        assert not home.exists()
        assert not home.parent.exists()
        assert f"feature/{NEXT}" not in git(main, "branch", "--list")

    def test_prune_puts_the_checkout_back_on_develop_once_every_ticket_is_merged(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        git(main, "checkout", "-b", SHARED_BRANCH)
        git(main, "commit", "--allow-empty", "-m", f"{NEXT}: work")
        git(main, "checkout", "develop")
        git(main, "merge", "--no-ff", SHARED_BRANCH, "-m", "merge")
        git(main, "checkout", SHARED_BRANCH)
        assert run(main, "prune").returncode == 0
        assert git(main, "branch", "--show-current") == "develop"
        assert SHARED_BRANCH not in git(main, "branch", "--list")

    def test_prune_keeps_the_shared_branch_while_a_ticket_runs(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        git(main, "checkout", "-b", SHARED_BRANCH)
        open_ticket(main, NEXT)
        assert run(main, "prune").returncode == 0
        assert git(main, "branch", "--show-current") == SHARED_BRANCH

    def test_setup_turns_on_the_gitflow_hooks(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        assert run(main, "setup").returncode == 0
        assert git(main, "config", "core.hooksPath") == ".githooks"
