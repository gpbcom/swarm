from __future__ import annotations

# Standard library imports
from pathlib import Path
from typing import List

# First-party imports
from tests.harness.tickets.helpers import (
    DONE,
    NEXT,
    add_remote,
    branch_with_commit,
    git,
    lines,
    make_repo,
    open_ticket,
    run,
)

MERGED = "feature/merged"
LIVE = "feature/live"
REPLAYED = "feature/replayed"
WORKER = "worktree-wf_old-1"
WORKER_OF_OPEN = "worktree-wf_open-2"
BACKUP_REFS = "refs/swarm-backup/"


def verdict(main: Path, branch: str) -> str:
    """Return the line of ``tickets.py branches`` that names ``branch``."""
    found = [line for line in lines(run(main, "branches")) if len(line.split()) > 1 and line.split()[1] == branch]
    assert len(found) == 1, found
    return found[0]


def local_branches(main: Path) -> List[str]:
    return git(main, "for-each-ref", "--format=%(refname:short)", "refs/heads").splitlines()


def bundles(main: Path) -> List[Path]:
    return sorted((main / ".git" / "swarm" / "backups").glob("*.bundle"))


def merged_branch(main: Path) -> None:
    branch_with_commit(main, MERGED, "merged.txt", "merged\n", "merged work")
    git(main, "merge", "-q", "--no-ff", MERGED, "-m", "merge")


def replayed_branch(main: Path) -> None:
    """A branch whose change reached develop under another commit, as after a history rewrite."""
    commit = branch_with_commit(main, REPLAYED, "replayed.txt", "replayed\n", "replayed work")
    git(main, "cherry-pick", "-x", commit)


def worker_with_a_discarded_attempt(main: Path, ticket: str, branch: str = WORKER) -> Path:
    """A worker branch of ``ticket`` holding a first attempt develop replaced, in its worktree with uncommitted work."""
    branch_with_commit(main, branch, "task.py", "first attempt\n", f"{ticket} K01: first attempt")
    worktree = main.parent / "worktrees" / branch
    git(main, "worktree", "add", "-q", str(worktree), branch)
    (worktree / "left.txt").write_text("uncommitted\n", encoding="utf-8")
    return worktree


class TestBranches:
    def test_each_branch_gets_a_verdict(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        merged_branch(main)
        replayed_branch(main)
        branch_with_commit(main, LIVE, "live.txt", "live\n", "work of its own")
        worker_with_a_discarded_attempt(main, DONE)
        result = run(main, "branches")
        assert result.returncode == 0, result.stderr
        assert "🔒" in verdict(main, "develop")
        assert "merged" in verdict(main, MERGED)
        assert "in develop" in verdict(main, REPLAYED)
        assert "superseded" in verdict(main, WORKER)
        assert "🌱" in verdict(main, LIVE)
        assert "rebase" in verdict(main, LIVE)

    def test_master_is_never_rebased_or_deleted(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        git(main, "branch", "master", "develop")
        assert "🔒" in verdict(main, "master")
        assert "release" in verdict(main, "master")
        assert run(main, "prune").returncode == 0
        assert "master" in local_branches(main)

    def test_a_worker_of_a_ticket_not_done_keeps_its_work(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        worker_with_a_discarded_attempt(main, NEXT)
        assert "🌱" in verdict(main, WORKER)
        assert run(main, "prune").returncode == 0
        assert WORKER in local_branches(main)

    def test_prune_deletes_what_develop_holds_and_keeps_live_work(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        merged_branch(main)
        replayed_branch(main)
        branch_with_commit(main, LIVE, "live.txt", "live\n", "work of its own")
        worktree = worker_with_a_discarded_attempt(main, DONE)
        result = run(main, "prune")
        assert result.returncode == 0, result.stderr
        remaining = local_branches(main)
        assert LIVE in remaining
        assert "develop" in remaining
        for gone in (MERGED, REPLAYED, WORKER):
            assert gone not in remaining
        assert not worktree.exists()

    def test_nothing_is_deleted_without_a_backup(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        merged_branch(main)
        worker_with_a_discarded_attempt(main, DONE)
        assert run(main, "prune").returncode == 0
        [bundle] = bundles(main)
        heads = git(main, "bundle", "list-heads", str(bundle))
        assert f"refs/heads/{MERGED}" in heads
        assert f"refs/heads/{WORKER}" in heads
        uncommitted = [line.split()[1] for line in heads.splitlines() if BACKUP_REFS in line]
        assert len(uncommitted) == 1
        git(main, "fetch", "-q", str(bundle), f"{uncommitted[0]}:refs/restored/worker")
        assert git(main, "show", "refs/restored/worker:left.txt") == "uncommitted"
        assert BACKUP_REFS not in git(main, "for-each-ref")

    def test_the_dry_run_changes_nothing(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        merged_branch(main)
        worktree = worker_with_a_discarded_attempt(main, DONE)
        result = run(main, "prune", "--dry-run")
        assert result.returncode == 0, result.stderr
        assert MERGED in result.stdout
        assert MERGED in local_branches(main)
        assert worktree.exists()
        assert not bundles(main)

    def test_workers_are_kept_while_a_ticket_is_open(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        worktree = worker_with_a_discarded_attempt(main, DONE, WORKER_OF_OPEN)
        open_ticket(main, NEXT)
        assert "🔄" in verdict(main, WORKER_OF_OPEN)
        assert run(main, "prune").returncode == 0
        assert WORKER_OF_OPEN in local_branches(main)
        assert worktree.exists()

    def test_a_branch_someone_works_on_in_a_worktree_is_kept(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        worktree = main.parent / "elsewhere"
        git(main, "worktree", "add", "-q", "-b", "feature/new-work", str(worktree), "develop")
        (worktree / "draft.txt").write_text("not committed yet\n", encoding="utf-8")
        assert "🔄" in verdict(main, "feature/new-work")
        assert run(main, "prune").returncode == 0
        assert "feature/new-work" in local_branches(main)
        assert (worktree / "draft.txt").exists()

    def test_prune_deletes_merged_branches_on_github_and_keeps_the_rest(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        merged_branch(main)
        branch_with_commit(main, LIVE, "live.txt", "live\n", "work of its own")
        remote = add_remote(main, MERGED, LIVE)
        result = run(main, "prune")
        assert result.returncode == 0, result.stderr
        left = git(remote, "for-each-ref", "--format=%(refname:short)", "refs/heads").splitlines()
        assert sorted(left) == sorted(["develop", "master", LIVE])

    def test_a_leftover_ticket_folder_of_a_done_ticket_is_saved_then_removed(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        leftover = main.parent / "main-tickets" / DONE
        leftover.mkdir(parents=True)
        (leftover / "swarm.code-workspace").write_text("{}\n", encoding="utf-8")
        assert run(main, "prune").returncode == 0
        assert not leftover.parent.exists()
        [bundle] = bundles(main)
        assert BACKUP_REFS in git(main, "bundle", "list-heads", str(bundle))
