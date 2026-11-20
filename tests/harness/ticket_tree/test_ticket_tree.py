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
    OTHER,
    PUSHED_KEY,
    REMAINING_KEY,
    SHARED_BRANCH,
    TICKET,
    TICKET_FOLDER,
    TICKET_TITLE,
    TREE_KEY,
    add_ticket,
    add_worktree,
    commit_count,
    documents_problems,
    git,
    integrated_repo,
    legacy_home,
    make_repo,
    run,
    run_json,
    task_args,
    worker_writes,
)

PATHS_KEY = "paths"


def two_tickets(tmp_path: Path) -> Path:
    """Prepare two tickets in the same checkout; each integrates one file of its own."""
    main = make_repo(tmp_path)
    add_ticket(main, OTHER)
    run_json(main, "prepare")
    assert run(main, "prepare", ticket=OTHER).returncode == 0
    worker_writes(main, "w1", "K01", {"src/mine.py": "x = 1\n"})
    run_json(main, "integrate", "--task", "K01")
    worker_writes(main, "w2", "K01", {"src/theirs.py": "y = 2\n"}, ticket=OTHER)
    assert run(main, "integrate", "--task", "K01", ticket=OTHER).returncode == 0
    return main


def with_remote(tmp_path: Path, main: Path) -> Path:
    remote = tmp_path / "remote.git"
    git(tmp_path, "init", "--bare", "-b", "develop", str(remote))
    git(main, "remote", "add", "origin", str(remote))
    git(main, "push", "origin", "develop")
    return remote


class TestTicketTree:
    def test_prepare_puts_the_main_checkout_on_the_shared_branch(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        (main / "stray.txt").write_text("the person's own work\n", encoding="utf-8")
        result = run_json(main, "prepare")
        assert result[HOME_KEY] == str(main)
        assert git(main, "branch", "--show-current") == SHARED_BRANCH
        assert (main / TICKET_FOLDER / "TICKET.md").is_file()
        assert (main / "stray.txt").is_file()
        assert not legacy_home(main).exists()

    def test_prepare_refuses_a_checkout_on_another_branch(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        git(main, "checkout", "-b", "feature/something-else")
        result = run(main, "prepare")
        assert result.returncode == 1
        assert SHARED_BRANCH in result.stderr

    def test_two_tickets_share_the_checkout_and_the_branch(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        add_ticket(main, OTHER)
        first = run_json(main, "prepare")
        second = run(main, "prepare", ticket=OTHER)
        assert second.returncode == 0, second.stderr
        assert first[HOME_KEY] == str(main)
        assert git(main, "branch", "--show-current") == SHARED_BRANCH
        assert (main / "docs" / "tickets" / OTHER / "TICKET.md").is_file()

    def test_prepare_run_again_keeps_the_ticket_s_state(self, tmp_path: Path) -> None:
        main = integrated_repo(tmp_path)
        assert run_json(main, "prepare")[INTEGRATED_KEY] == ["K01"]

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
        (main / "earlier.txt").write_text("integrated earlier\n", encoding="utf-8")
        worker = add_worktree(main, "w1")
        run_json(worker, "start")
        assert (worker / "earlier.txt").read_text(encoding="utf-8") == "integrated earlier\n"
        assert (worker / TICKET_FOLDER / "TICKET.md").is_file()

    def test_start_refuses_the_main_checkout(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        run_json(main, "prepare")
        assert run(main, "start").returncode == 1

    def test_a_worker_created_from_another_commit_moves_to_the_ticket_base(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        run_json(main, "prepare")
        (main / "later.txt").write_text("committed by an earlier ticket\n", encoding="utf-8")
        git(main, "add", "later.txt")
        git(main, "commit", "-m", "T9.00: an earlier ticket")
        worker = add_worktree(main, "w1", "develop")
        run_json(worker, "start")
        assert git(worker, "rev-parse", "HEAD") == git(main, "rev-parse", "HEAD")
        assert (worker / "later.txt").is_file()

    def test_a_wave_is_integrated_in_order_without_any_commit(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        run_json(main, "prepare")
        first = worker_writes(main, "w1", "K01", {"a.txt": "a\nB\nc\n"})
        worker_writes(main, "w2", "K02", {"src/new.py": "x = 1\n"})
        result = run_json(main, "integrate", *task_args(["K01", "K02"]))
        assert result[INTEGRATED_KEY] == ["K01", "K02"]
        assert result[CONFLICTS_KEY] == []
        assert (main / "a.txt").read_text(encoding="utf-8") == "a\nB\nc\n"
        assert (main / "src" / "new.py").is_file()
        assert commit_count(main, SHARED_BRANCH) == 1
        assert not first.exists()
        assert run_json(main, "status")[INTEGRATED_KEY] == ["K01", "K02"]

    def test_integrate_records_the_ticket_s_own_files(self, tmp_path: Path) -> None:
        main = two_tickets(tmp_path)
        mine = run_json(main, "status")[PATHS_KEY]
        assert isinstance(mine, list)
        assert "src/mine.py" in mine
        assert f"{TICKET_FOLDER}/" in mine
        assert "src/theirs.py" not in mine

    def test_diff_and_changes_show_only_the_ticket_s_own_files(self, tmp_path: Path) -> None:
        main = two_tickets(tmp_path)
        names = run(main, "diff", "--name-only").stdout
        assert "src/mine.py" in names
        assert "src/theirs.py" not in names
        assert OTHER not in names
        table = run(main, "changes").stdout
        assert "src/mine.py" in table
        assert "src/theirs.py" not in table

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
        assert (main / "a.txt.rej").is_file()
        assert run(main, "integrate", "--task", "K02", "--resolved").returncode == 1
        (main / "a.txt.rej").unlink()
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
        assert commit_count(main, SHARED_BRANCH) == 1

    def test_finish_commits_only_the_ticket_s_files_and_leaves_the_other_ticket_uncommitted(
        self, tmp_path: Path
    ) -> None:
        main = two_tickets(tmp_path)
        assert documents_problems(main, "In [`src/mine.py:1`](../../../src/mine.py#L1).", "") == ""
        result = run_json(main, "finish")
        commit = str(result[COMMIT_KEY])
        committed = git(main, "show", "--name-only", "--format=", commit).splitlines()
        assert "src/mine.py" in committed
        assert f"{TICKET_FOLDER}/EXPLAIN.md" in committed
        assert "src/theirs.py" not in committed
        assert not any(name.startswith(f"docs/tickets/{OTHER}") for name in committed)
        assert git(main, "log", "-1", "--format=%s", commit) == TICKET_TITLE
        assert (main / "src" / "theirs.py").is_file()
        assert "src/theirs.py" in git(main, "status", "--porcelain")
        assert git(main, "diff", "--cached", "--name-only") == ""
        assert git(main, "branch", "--show-current") == SHARED_BRANCH

    def test_finish_without_a_remote_merges_the_shared_branch_into_develop(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        run_json(main, "prepare")
        worker_writes(main, "w1", "K01", {"src/new.py": "x = 1\n"})
        run_json(main, "integrate", "--task", "K01")
        assert documents_problems(main, "In [`src/new.py:1`](../../../src/new.py#L1).", "") == ""
        result = run_json(main, "finish")
        assert result[PUSHED_KEY] is False
        assert git(main, "rev-parse", "develop") == result[MERGE_KEY]
        assert git(main, "show", "develop:src/new.py") == "x = 1"
        assert git(main, "status", "--porcelain") == ""
        assert run_json(main, "status")[INTEGRATED_KEY] == []

    def test_finish_with_a_remote_pushes_the_shared_branch_and_leaves_develop_to_the_pull_request(
        self, tmp_path: Path
    ) -> None:
        main = make_repo(tmp_path)
        remote = with_remote(tmp_path, main)
        run_json(main, "prepare")
        worker_writes(main, "w1", "K01", {"src/new.py": "x = 1\n"})
        run_json(main, "integrate", "--task", "K01")
        assert documents_problems(main, "In [`src/new.py:1`](../../../src/new.py#L1).", "") == ""
        result = run(main, "finish", "--no-pull-request")
        assert result.returncode == 0, result.stderr
        assert git(remote, "rev-parse", SHARED_BRANCH) == git(main, "rev-parse", SHARED_BRANCH)
        assert git(remote, "rev-parse", "develop") == git(main, "rev-parse", "develop")
        assert commit_count(main, "develop") == 1

    def test_two_finishes_give_two_commits_on_the_shared_branch(self, tmp_path: Path) -> None:
        main = two_tickets(tmp_path)
        with_remote(tmp_path, main)
        assert documents_problems(main, "In [`src/mine.py:1`](../../../src/mine.py#L1).", "") == ""
        assert run(main, "finish", "--no-pull-request").returncode == 0
        other_explain = main / "docs" / "tickets" / OTHER / "EXPLAIN.md"
        other_explain.write_text(
            "# Explain\n\nIn [`src/theirs.py:1`](../../../src/theirs.py#L1).\n\n<!-- changes -->\n<!-- /changes -->\n",
            encoding="utf-8",
        )
        assert run(main, "changes", "--write", ticket=OTHER).returncode == 0
        second = run(main, "finish", "--no-pull-request", ticket=OTHER)
        assert second.returncode == 0, second.stderr
        subjects = git(main, "log", "--format=%s", f"develop..{SHARED_BRANCH}").splitlines()
        assert subjects == [f"{OTHER}: Second ticket", TICKET_TITLE]
        assert git(main, "status", "--porcelain") == ""

    def test_a_ticket_started_in_its_own_worktree_before_tkt_16_keeps_it(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        git(main, "worktree", "add", "-b", f"feature/{TICKET}", str(legacy_home(main)), "develop")
        assert run_json(main, "home")[HOME_KEY] == str(legacy_home(main))
