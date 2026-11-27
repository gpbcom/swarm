from __future__ import annotations

# Standard library imports
from pathlib import Path

# First-party imports
from tests.harness.ticket_tree.helpers import SHARED_BRANCH, git, make_repo, run

PLANNED = "docs/tickets/T9.05/PLAN.md"
LESSONS = "docs/tickets/LESSONS.md"
BOARD_CACHE = ".claude/github.json"
OTHER_FILE = "a.txt"
HARNESS_FILE = ".claude/scripts/tickets/tickets.py"
SECOND_TICKET = "T9.06"


def commit_harness_files(main: Path) -> None:
    """Commit a plan, the lessons and the board cache on develop, as earlier tickets left them."""
    for relative in (PLANNED, LESSONS, BOARD_CACHE):
        path = main / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("before\n", encoding="utf-8")
        git(main, "add", relative)
    git(main, "commit", "-m", "harness files")


def change(main: Path, relative: str) -> None:
    (main / relative).write_text("after\n", encoding="utf-8")


class TestTicketTreePrepare:
    def test_prepare_carries_the_plans_and_the_board_cache_written_on_develop(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        commit_harness_files(main)
        for relative in (PLANNED, LESSONS, BOARD_CACHE):
            change(main, relative)
        result = run(main, "prepare")
        assert result.returncode == 0, result.stderr
        assert git(main, "branch", "--show-current") == SHARED_BRANCH
        for relative in (PLANNED, LESSONS, BOARD_CACHE):
            assert (main / relative).read_text(encoding="utf-8") == "after\n", relative
        assert sorted(git(main, "diff", "--name-only").splitlines()) == sorted([BOARD_CACHE, LESSONS, PLANNED])

    def test_prepare_still_refuses_any_other_change_on_develop(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        commit_harness_files(main)
        change(main, PLANNED)
        change(main, OTHER_FILE)
        result = run(main, "prepare")
        assert result.returncode == 1
        assert OTHER_FILE in result.stderr
        assert PLANNED not in result.stderr.split("(", 1)[1].split(")", 1)[0]
        assert git(main, "branch", "--show-current") == "develop"
        assert (main / OTHER_FILE).read_text(encoding="utf-8") == "after\n"

    def develop_moves(self, main: Path, tmp_path: Path, relative: str) -> None:
        """Commit a change on develop while the main checkout stays on the shared branch, as a merged pull request does."""
        other = tmp_path / "develop-checkout"
        git(main, "worktree", "add", "--quiet", str(other), "develop")
        (other / relative).parent.mkdir(parents=True, exist_ok=True)
        (other / relative).write_text("newer\n", encoding="utf-8")
        git(other, "add", relative)
        git(other, "commit", "-m", "develop moves")
        git(main, "worktree", "remove", "--force", str(other))

    def test_a_new_ticket_is_refused_while_develop_holds_a_newer_harness(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        assert run(main, "prepare").returncode == 0
        self.develop_moves(main, tmp_path, HARNESS_FILE)
        refused = run(main, "prepare", ticket=SECOND_TICKET)
        assert refused.returncode == 1
        assert "L-54" in refused.stderr
        assert HARNESS_FILE in refused.stderr

    def test_an_open_ticket_still_continues_and_a_change_outside_the_harness_does_not_hold_a_start(
        self, tmp_path: Path
    ) -> None:
        main = make_repo(tmp_path)
        assert run(main, "prepare").returncode == 0
        self.develop_moves(main, tmp_path, "docs/other.md")
        assert run(main, "prepare", ticket=SECOND_TICKET).returncode == 0
        self.develop_moves(main, tmp_path, HARNESS_FILE)
        continued = run(main, "prepare")
        assert continued.returncode == 0, continued.stderr
