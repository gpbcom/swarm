from __future__ import annotations

from pathlib import Path

import pytest

from tests.harness.ticket_tree.helpers import (
    COMMIT_KEY,
    CONFLICTS_KEY,
    HOME_KEY,
    INTEGRATED_KEY,
    LEGACY_BRANCH,
    MERGE_KEY,
    PUSHED_KEY,
    REMAINING_KEY,
    TICKET,
    TICKET_BRANCH,
    TICKET_FOLDER,
    TICKET_TITLE,
    TREE_KEY,
    add_worktree,
    commit_count,
    documents_problems,
    git,
    home,
    integrated_repo,
    make_repo,
    run,
    run_json,
    task_args,
    worker_writes,
)


class TestTicketTree:
    def test_prepare_gives_the_ticket_its_own_worktree_and_leaves_the_main_checkout_on_develop(
        self, tmp_path: Path
    ) -> None:
        main = make_repo(tmp_path)
        (main / "stray.txt").write_text("the person's own work\n", encoding="utf-8")
        result = run_json(main, "prepare")
        assert result[HOME_KEY] == str(home(main))
        assert git(main, "branch", "--show-current") == "develop"
        assert git(home(main), "branch", "--show-current") == TICKET_BRANCH
        assert (main / "stray.txt").is_file()
        assert not (home(main) / "stray.txt").exists()

    def test_prepare_moves_the_ticket_folder_into_the_ticket_worktree(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        run_json(main, "prepare")
        assert (home(main) / TICKET_FOLDER / "TICKET.md").is_file()
        assert not (main / TICKET_FOLDER).exists()
        assert commit_count(main, TICKET_BRANCH) == 1

    def test_prepare_run_again_keeps_the_same_worktree(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        run_json(main, "prepare")
        assert run_json(main, "prepare")[HOME_KEY] == str(home(main))
        assert run_json(home(main), "prepare")[HOME_KEY] == str(home(main))

    def test_two_tickets_get_two_worktrees(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        other = main / "docs" / "tickets" / "T9.02"
        other.mkdir(parents=True)
        (other / "TICKET.md").write_text("# T9.02: Second ticket\n", encoding="utf-8")
        run_json(main, "prepare")
        second = run(main, "prepare", ticket="T9.02")
        assert second.returncode == 0, second.stderr
        assert git(main, "branch", "--show-current") == "develop"
        assert (home(main).parent / "T9.02" / "docs" / "tickets" / "T9.02" / "TICKET.md").is_file()

    def test_status_without_a_run_lists_no_task(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        assert run_json(main, "status")[INTEGRATED_KEY] == []

    def test_status_counts_the_task_commits_of_a_run_before_tkt_5(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        git(main, "checkout", "-b", LEGACY_BRANCH)
        (main / "old.txt").write_text("from an earlier run\n", encoding="utf-8")
        git(main, "add", "old.txt")
        git(main, "commit", "-m", f"{TICKET} K01: an earlier task")
        assert run_json(main, "status")[INTEGRATED_KEY] == ["K01"]

    def test_start_copies_the_uncommitted_work_into_a_worker(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        run_json(main, "prepare")
        (home(main) / "earlier.txt").write_text("integrated earlier\n", encoding="utf-8")
        worker = add_worktree(main, "w1")
        run_json(worker, "start")
        assert (worker / "earlier.txt").read_text(encoding="utf-8") == "integrated earlier\n"
        assert (worker / TICKET_FOLDER / "TICKET.md").is_file()

    def test_start_refuses_the_main_checkout_and_the_ticket_worktree(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        run_json(main, "prepare")
        assert run(main, "start").returncode == 1
        assert run(home(main), "start").returncode == 1

    def test_a_worker_created_from_another_commit_moves_to_the_ticket_base(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        run_json(main, "prepare")
        (main / "later.txt").write_text("merged by another ticket\n", encoding="utf-8")
        git(main, "add", "later.txt")
        git(main, "commit", "-m", "another ticket")
        worker = add_worktree(main, "w1")
        run_json(worker, "start")
        assert git(worker, "rev-parse", "HEAD") == git(home(main), "rev-parse", "HEAD")
        assert not (worker / "later.txt").exists()
        assert (worker / TICKET_FOLDER / "TICKET.md").is_file()

    def test_a_wave_is_integrated_in_order_without_any_commit(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        run_json(main, "prepare")
        first = worker_writes(main, "w1", "K01", {"a.txt": "a\nB\nc\n"})
        worker_writes(main, "w2", "K02", {"src/new.py": "x = 1\n"})
        result = run_json(main, "integrate", *task_args(["K01", "K02"]))
        assert result[INTEGRATED_KEY] == ["K01", "K02"]
        assert result[CONFLICTS_KEY] == []
        assert (home(main) / "a.txt").read_text(encoding="utf-8") == "a\nB\nc\n"
        assert (home(main) / "src" / "new.py").is_file()
        assert (main / "a.txt").read_text(encoding="utf-8") == "a\nb\nc\n"
        assert commit_count(main, TICKET_BRANCH) == 1
        assert not first.exists()
        assert run_json(main, "status")[INTEGRATED_KEY] == ["K01", "K02"]

    def test_the_next_wave_starts_from_the_integrated_work(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        run_json(main, "prepare")
        worker_writes(main, "w1", "K01", {"src/new.py": "x = 1\n"})
        run_json(main, "integrate", "--task", "K01")
        second = add_worktree(main, "w2")
        run_json(second, "start")
        assert (second / "src" / "new.py").read_text(encoding="utf-8") == "x = 1\n"

    def test_a_conflict_stops_the_integration_until_it_is_resolved(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        run_json(main, "prepare")
        worker_writes(main, "w1", "K01", {"a.txt": "a\nX\nc\n"})
        worker_writes(main, "w2", "K02", {"a.txt": "a\nY\nc\n"})
        result = run(main, "integrate", *task_args(["K01", "K02"]))
        assert result.returncode == 1
        assert (home(main) / "a.txt.rej").is_file()
        assert run(main, "integrate", "--task", "K02", "--resolved").returncode == 1
        (home(main) / "a.txt.rej").unlink()
        resolved = run_json(main, "integrate", "--task", "K02", "--resolved")
        assert resolved[INTEGRATED_KEY] == ["K02"]
        assert resolved[REMAINING_KEY] == []

    def test_diff_from_an_earlier_tree_shows_only_the_later_work(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        run_json(main, "prepare")
        worker_writes(main, "w1", "K01", {"one.txt": "1\n"})
        tree = run_json(main, "integrate", "--task", "K01")[TREE_KEY]
        worker_writes(main, "w2", "K02", {"two.txt": "2\n"})
        run_json(main, "integrate", "--task", "K02")
        names = run(main, "diff", "--from", str(tree), "--name-only").stdout
        assert "two.txt" in names
        assert "one.txt" not in names

    def test_the_changes_table_lists_files_and_lines_but_not_the_ticket_folder(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        run_json(main, "prepare")
        worker_writes(main, "w1", "K01", {"a.txt": "a\nB\nc\nd\n"})
        run_json(main, "integrate", "--task", "K01")
        table = run(main, "changes").stdout
        assert "| [`a.txt`](../../../a.txt) | Modified | [2](../../../a.txt#L2), [4](../../../a.txt#L4) |" in table

        assert TICKET_FOLDER not in table
        assert run(main, "changes", "--check").returncode == 1
        assert run(main, "changes", "--write").returncode == 0
        assert run(main, "changes", "--check").returncode == 0

    def test_removed_lines_are_clickable_in_the_changes_table(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        run_json(main, "prepare")
        worker_writes(main, "w1", "K01", {"a.txt": "a\nc\n"})
        run_json(main, "integrate", "--task", "K01")
        assert "[removed after 1](../../../a.txt#L1)" in run(main, "changes").stdout

    def test_clickable_documents_pass_the_docs_check(self, tmp_path: Path) -> None:
        main = integrated_repo(tmp_path)
        explain = "1. **Step:** in [`a.txt:2`](../../../a.txt#L2), see [`a.txt`](../../../a.txt) lines 2-4."
        implementation = "**Where:** [`a.txt:4`](../../../a.txt#L4) · [TICKET.md](TICKET.md)"
        assert documents_problems(main, explain, implementation) == ""
        assert run(main, "docs").returncode == 0

    @pytest.mark.parametrize(
        "explain, problem",
        [
            ("Read `a.txt:2` first.", "`a.txt:2` is not clickable"),
            ("Read `a.txt` first.", "`a.txt` is not clickable"),
            ("Read a.txt:2 first.", "a.txt:2 is not clickable"),
            ("See [`b.txt:1`](../../../b.txt#L1).", "does not exist"),
            ("See [`a.txt:9`](../../../a.txt#L9).", "which has 4 lines"),
            ("See [`a.txt:2`](../../../a.txt#L3).", "names line 2 but the link opens line 3"),
            ("See [`a.txt`](../../../a.txt#top).", "must point at a line"),
            ("Left: {{path}}.", "placeholder"),
        ],
    )
    def test_a_file_or_line_that_is_not_a_working_link_is_reported(
        self, tmp_path: Path, explain: str, problem: str
    ) -> None:
        main = integrated_repo(tmp_path)
        assert problem in documents_problems(main, explain, "")
        assert run(main, "docs").returncode == 1

    def test_paths_in_code_blocks_and_comments_are_commands_not_references(self, tmp_path: Path) -> None:
        main = integrated_repo(tmp_path)
        explain = "<!-- `a.txt:2` -->\n\n```bash\ncat a.txt\n```"
        assert documents_problems(main, explain, "") == ""

    def test_finish_refuses_documents_with_a_link_that_does_not_work(self, tmp_path: Path) -> None:
        main = integrated_repo(tmp_path)
        documents_problems(main, "Read `a.txt:2`.", "")
        result = run(main, "finish")
        assert result.returncode == 1
        assert "not clickable" in result.stderr
        assert commit_count(main, TICKET_BRANCH) == 1

    def test_finish_without_a_remote_makes_one_commit_and_merges_it_into_develop(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        run_json(main, "prepare")
        worker_writes(main, "w1", "K01", {"src/new.py": "x = 1\n"})
        run_json(main, "integrate", "--task", "K01")
        assert documents_problems(main, "In [`src/new.py:1`](../../../src/new.py#L1).", "") == ""
        result = run_json(main, "finish")
        assert result[PUSHED_KEY] is False
        assert git(main, "log", "-1", "--format=%s", str(result[COMMIT_KEY])) == TICKET_TITLE
        assert commit_count(main, TICKET_BRANCH) == 2
        assert git(main, "rev-parse", "develop") == result[MERGE_KEY]
        assert (main / "src" / "new.py").is_file()
        assert git(main, "status", "--porcelain") == ""
        assert run_json(main, "status")[INTEGRATED_KEY] == []

    def test_finish_with_a_remote_pushes_the_feature_branch_and_leaves_develop_to_the_pull_request(
        self, tmp_path: Path
    ) -> None:
        main = make_repo(tmp_path)
        remote = tmp_path / "remote.git"
        git(tmp_path, "init", "--bare", "-b", "develop", str(remote))
        git(main, "remote", "add", "origin", str(remote))
        git(main, "push", "origin", "develop")
        run_json(main, "prepare")
        worker_writes(main, "w1", "K01", {"src/new.py": "x = 1\n"})
        run_json(main, "integrate", "--task", "K01")
        assert documents_problems(main, "In [`src/new.py:1`](../../../src/new.py#L1).", "") == ""
        result = run(main, "finish", "--no-pull-request")
        assert result.returncode == 0, result.stderr
        assert git(remote, "rev-parse", TICKET_BRANCH) == git(home(main), "rev-parse", "HEAD")
        assert git(remote, "rev-parse", "develop") == git(main, "rev-parse", "develop")
        assert commit_count(main, "develop") == 1
