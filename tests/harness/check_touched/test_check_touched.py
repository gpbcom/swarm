from __future__ import annotations

from pathlib import Path
from typing import ClassVar, Dict

import pytest
from pydantic import JsonValue

from tests.harness.check_touched.helpers import (
    COUNTER_NAME,
    add_worktree,
    catalogue_text,
    echo_rule,
    failing_rule,
    git,
    git_dir,
    make_repo,
    run_hook,
    run_ticket_tree,
)


class TestCheckTouched:
    GHOST_RULE: ClassVar[Dict[str, JsonValue]] = {
        "name": "ghost",
        "match": r"\.txt$",
        "run": ["swarm-no-such-executable-xyz", "{files}"],
    }

    def test_the_main_working_tree_is_not_checked(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path, catalogue_text([failing_rule()]))
        (main / "bad.txt").write_text("FAIL\n", encoding="utf-8")
        result = run_hook(main)
        assert result.returncode == 0
        assert result.stdout == ""
        assert result.stderr == ""

    def test_a_directory_outside_git_is_not_checked(self, tmp_path: Path) -> None:
        outside = tmp_path / "outside"
        outside.mkdir()
        result = run_hook(outside)
        assert result.returncode == 0
        assert result.stdout == ""
        assert result.stderr == ""

    def test_a_worktree_without_changes_passes(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path, catalogue_text([failing_rule()]))
        worker = add_worktree(main, tmp_path)
        result = run_hook(worker)
        assert result.returncode == 0
        assert "❌" not in result.stderr

    def test_a_failing_check_blocks_twice_then_lets_the_agent_go(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path, catalogue_text([failing_rule()], max_blocks=2))
        worker = add_worktree(main, tmp_path)
        (worker / "bad.txt").write_text("FAIL\n", encoding="utf-8")
        for _ in range(2):
            result = run_hook(worker)
            assert result.returncode == 2
            assert "❌" in result.stderr
            assert "no-fail" in result.stderr
        third = run_hook(worker)
        assert third.returncode == 0

    def test_a_fixed_file_passes_and_clears_the_counter(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path, catalogue_text([failing_rule()]))
        worker = add_worktree(main, tmp_path)
        (worker / "bad.txt").write_text("FAIL\n", encoding="utf-8")
        assert run_hook(worker).returncode == 2
        assert (git_dir(worker) / COUNTER_NAME).exists()
        (worker / "bad.txt").write_text("fine\n", encoding="utf-8")
        assert run_hook(worker).returncode == 0
        assert not (git_dir(worker) / COUNTER_NAME).exists()

    def test_a_missing_executable_is_not_a_failure(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path, catalogue_text([self.GHOST_RULE]))
        worker = add_worktree(main, tmp_path)
        (worker / "a.txt").write_text("a\n", encoding="utf-8")
        result = run_hook(worker)
        assert result.returncode == 0
        assert "❌" not in result.stderr

    def test_committed_and_uncommitted_changes_are_seen_but_not_older_files(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path, catalogue_text([echo_rule()]))
        git(main, "branch", "ticket/T9.99", "develop")
        worker = add_worktree(main, tmp_path)
        (worker / "a.txt").write_text("a\n", encoding="utf-8")
        git(worker, "add", "a.txt")
        git(worker, "commit", "-m", "T9.99 K01: x")
        (worker / "b.txt").write_text("b\n", encoding="utf-8")
        result = run_hook(worker, "--dry-run")
        assert result.returncode == 0
        assert "seen: echo a.txt b.txt" in result.stdout.splitlines()
        assert "old.txt" not in result.stdout

    def test_after_start_only_the_worker_s_own_changes_are_checked(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path, catalogue_text([echo_rule()]))
        home = tmp_path / "main-tickets" / "T9.99"
        git(main, "worktree", "add", "-b", "feature/T9.99", str(home), "develop")
        (home / "earlier.txt").write_text("integrated, not committed\n", encoding="utf-8")
        worker = add_worktree(main, tmp_path)
        assert run_ticket_tree(worker, "start", "--ticket", "T9.99").returncode == 0
        assert (worker / "earlier.txt").is_file()
        (worker / "mine.txt").write_text("mine\n", encoding="utf-8")
        result = run_hook(worker, "--dry-run")
        assert result.returncode == 0
        assert "seen: echo mine.txt" in result.stdout.splitlines()

    def test_a_dry_run_runs_nothing(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path, catalogue_text([failing_rule()]))
        worker = add_worktree(main, tmp_path)
        (worker / "bad.txt").write_text("FAIL\n", encoding="utf-8")
        result = run_hook(worker, "--dry-run")
        assert result.returncode == 0
        assert "no-fail: " in result.stdout
        assert not (git_dir(worker) / COUNTER_NAME).exists()

    def test_a_service_source_change_lists_its_python_checks(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path, None)
        worker = add_worktree(main, tmp_path)
        source = worker / "services" / "demo" / "src" / "demo" / "service" / "x" / "y.py"
        source.parent.mkdir(parents=True)
        source.write_text("x = 1\n", encoding="utf-8")
        relative = "services/demo/src/demo/service/x/y.py"
        before = run_hook(worker, "--dry-run").stdout.splitlines()
        assert any(line.endswith(f"uv run ruff check {relative}") for line in before)
        assert any(line.endswith(f"uv run ruff format --check {relative}") for line in before)
        assert any(line.endswith("uv run mypy services/demo/src") for line in before)
        assert not any("pytest" in line for line in before)
        (worker / "services" / "demo" / "tests" / "service" / "x").mkdir(parents=True)
        after = run_hook(worker, "--dry-run").stdout.splitlines()
        assert any(line.endswith("uv run pytest services/demo/tests/service/x -n 2") for line in after)

    def test_a_change_only_under_tests_lists_ruff_but_no_pytest(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path, None)
        worker = add_worktree(main, tmp_path)
        test_file = worker / "services" / "demo" / "tests" / "service" / "x" / "test_y.py"
        test_file.parent.mkdir(parents=True)
        test_file.write_text("x = 1\n", encoding="utf-8")
        output = run_hook(worker, "--dry-run").stdout
        assert "uv run ruff check services/demo/tests/service/x/test_y.py" in output
        assert "pytest" not in output

    def test_a_specification_change_lists_the_specs_check(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path, None)
        worker = add_worktree(main, tmp_path)
        page = worker / "docs" / "specs" / "x.md"
        page.parent.mkdir(parents=True)
        page.write_text("# x\n", encoding="utf-8")
        output = run_hook(worker, "--dry-run").stdout
        assert "python3 .claude/skills/write-specs/scripts/specs.py check" in output

    @pytest.mark.parametrize("path", [".claude/hooks/x.py", ".claude/scripts/x.py"])
    def test_a_harness_script_change_lists_its_tests_only_when_they_exist(self, tmp_path: Path, path: str) -> None:
        main = make_repo(tmp_path, None)
        worker = add_worktree(main, tmp_path)
        script = worker / path
        script.parent.mkdir(parents=True, exist_ok=True)
        script.write_text("x = 1\n", encoding="utf-8")
        assert "pytest" not in run_hook(worker, "--dry-run").stdout
        (worker / "tests" / "harness" / "x").mkdir(parents=True)
        assert "uv run pytest tests/harness/x -n 2" in run_hook(worker, "--dry-run").stdout
