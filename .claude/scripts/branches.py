#!/usr/bin/env python3
from __future__ import annotations

import shutil
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set

sys.path.insert(0, str(Path(__file__).resolve().parent))

from ticket_tree import (
    BRANCH_PREFIX,
    LEGACY_PREFIX,
    REMOTE,
    SHARED_BRANCH,
    STATE_FOLDER,
    TICKET_PATTERN,
    TICKET_SUBJECT,
    WORKTREE_BRANCH_PREFIX,
    common_dir,
    git,
    has_remote,
    tickets_root,
    worktrees,
)

PROTECTED = ("develop", "master", "main")
PROTECTED_REASON = {
    "develop": "the base every branch is rebased on: it changes only through pull requests",
    "master": "never rebased, reset or deleted: it changes only through a release or a hotfix pull request (TKT-15)",
    "main": "never rebased, reset or deleted",
}
PROTECTED_KIND = "protected"
OPEN = "open"
MERGED = "merged"
INTEGRATED = "integrated"
SUPERSEDED = "superseded"
LIVE = "live"
DELETABLE = (MERGED, INTEGRATED, SUPERSEDED)
ICON = {PROTECTED_KIND: "🔒", OPEN: "🔄", MERGED: "🧹", INTEGRATED: "🧹", SUPERSEDED: "🧹", LIVE: "🌱"}
FOLDER_ICON = "📁"
BACKUPS = "backups"
BACKUP_REFS = "refs/swarm-backup"
REMOTE_PREFIX = f"refs/remotes/{REMOTE}/"


@dataclass
class Verdict:
    """What to do with one branch, or with one leftover ticket folder."""

    name: str
    kind: str
    reason: str
    remote: bool = False
    worktree: Optional[Path] = None
    folder: Optional[Path] = None

    @property
    def label(self) -> str:
        if self.folder is not None:
            return str(self.folder)
        return f"{REMOTE}/{self.name}" if self.remote else self.name

    @property
    def deletable(self) -> bool:
        return self.kind in DELETABLE


#####################
# Reading branches  #
#####################


def own_commits(main: Path, ref: str, branch: str) -> List[str]:
    """Return the subjects of the commits of ``branch`` whose change is not in ``ref`` (``git cherry``)."""
    output = git(main, "cherry", "-v", ref, branch, check=False)[1]
    return [line[2:].split(" ", 1)[-1] for line in output.splitlines() if line.startswith("+ ")]


def ticket_of_branch(branch: str) -> str:
    """Return the ticket of a ``feature/<ID>`` or ``ticket/<ID>`` branch, or an empty string."""
    for prefix in (BRANCH_PREFIX, LEGACY_PREFIX):
        if branch.startswith(prefix) and TICKET_PATTERN.match(branch[len(prefix) :]):
            return branch[len(prefix) :]
    return ""


def judge(main: Path, ref: str, branch: str, done: Set[str], open_ids: Set[str], remote: bool) -> Verdict:
    """Return the verdict of one branch (see the module docstring)."""
    name = branch
    target = f"{REMOTE}/{branch}" if remote else branch
    ticket = ticket_of_branch(branch)
    worker = branch.startswith(WORKTREE_BRANCH_PREFIX)
    if branch in PROTECTED:
        return Verdict(name, PROTECTED_KIND, PROTECTED_REASON[branch], remote)
    if branch == SHARED_BRANCH and open_ids:
        return Verdict(name, OPEN, f"shared by the open tickets {', '.join(sorted(open_ids))}", remote)
    if ticket and ticket in open_ids:
        return Verdict(name, OPEN, f"the branch of the open ticket {ticket}", remote)
    if worker and open_ids and not remote:
        return Verdict(name, OPEN, "a ticket is open: its workers may be running", remote)
    if git(main, "merge-base", "--is-ancestor", target, ref, check=False)[0] == 0:
        return Verdict(name, MERGED, f"merged into {ref}: delete", remote)
    subjects = own_commits(main, ref, target)
    if not subjects:
        return Verdict(
            name, INTEGRATED, f"its changes are already in develop ({ref}) under other commits: delete", remote
        )
    tickets = {match.group(1) for match in map(TICKET_SUBJECT.match, subjects) if match}
    every_one_of_a_ticket = len(tickets) > 0 and all(TICKET_SUBJECT.match(subject) for subject in subjects)
    if (worker or ticket) and every_one_of_a_ticket and tickets <= done:
        return Verdict(
            name,
            SUPERSEDED,
            f"{len(subjects)} attempt(s) of the done ticket(s) {', '.join(sorted(tickets))}, replaced in develop: "
            "delete, never rebase",
            remote,
        )
    return Verdict(name, LIVE, f"{len(subjects)} commit(s) of its own: rebase onto {ref}", remote)


def classify(main: Path, ref: str, done: Set[str], open_ids: Set[str]) -> List[Verdict]:
    """Return the verdict of every local branch, every branch on GitHub and every leftover ticket folder."""
    checked_out: Dict[str, Path] = {branch: path for path, branch in worktrees(main) if branch}
    current = git(main, "branch", "--show-current")[1]
    found: List[Verdict] = []
    local = git(main, "for-each-ref", "--format=%(refname:short)", "refs/heads")[1].splitlines()
    for branch in sorted(local):
        verdict = judge(main, ref, branch, done, open_ids, remote=False)
        if branch == current and verdict.kind not in (PROTECTED_KIND, OPEN):
            verdict = Verdict(branch, OPEN, "checked out in the main checkout")
        path = checked_out.get(branch)
        if path is not None and path.resolve() != main.resolve():
            verdict.worktree = path
            elsewhere = not branch.startswith(WORKTREE_BRANCH_PREFIX) and verdict.kind != PROTECTED_KIND
            if elsewhere:
                verdict = Verdict(branch, OPEN, f"checked out in {path}: someone works on it", worktree=path)
        found.append(verdict)
    remote_refs = git(main, "for-each-ref", "--format=%(refname)", REMOTE_PREFIX)[1].splitlines()
    for refname in sorted(remote_refs):
        branch = refname[len(REMOTE_PREFIX) :]
        if branch == "HEAD" or branch in PROTECTED:
            continue
        found.append(judge(main, ref, branch, done, open_ids, remote=True))
    linked = {path.resolve() for path, _ in worktrees(main)}
    root = tickets_root(main)
    if root.is_dir():
        for folder in sorted(root.iterdir()):
            if folder.is_dir() and folder.resolve() not in linked and folder.name in done:
                found.append(
                    Verdict(folder.name, SUPERSEDED, "leftover folder of a done ticket: delete", folder=folder)
                )
    return found


def show(verdicts: List[Verdict], ref: str) -> None:
    """Print one line per branch, with its icon and what to do."""
    print(f"🌿 Branches against {ref}")
    for verdict in verdicts:
        icon = FOLDER_ICON if verdict.folder is not None else ICON[verdict.kind]
        where = f" · 📂 {verdict.worktree}" if verdict.worktree is not None else ""
        print(f"  {icon} {verdict.label} · {verdict.kind}: {verdict.reason}{where}")
    counts: Dict[str, int] = {}
    for verdict in verdicts:
        counts[verdict.kind] = counts.get(verdict.kind, 0) + 1
    print("  " + " · ".join(f"{ICON[kind]} {kind} {count}" for kind, count in sorted(counts.items())))


##########
# Backup #
##########


def snapshot_commit(main: Path, folder: Path, parent: Optional[str], message: str) -> str:
    """Return a commit of every file of ``folder`` (ignored files excepted), on a temporary index: nothing is staged."""
    with tempfile.TemporaryDirectory() as scratch:
        index = Path(scratch) / "index"
        tree_git = ["--git-dir", str(common_dir(main)), "--work-tree", str(folder)]
        if parent:
            git(main, *tree_git, "read-tree", parent, index=index)
        git(main, *tree_git, "add", "-A", ".", index=index)
        tree = git(main, *tree_git, "write-tree", index=index)[1]
    parents = ["-p", parent] if parent else []
    return git(main, "commit-tree", tree, *parents, "-m", message)[1]


def has_uncommitted_work(folder: Path) -> bool:
    return bool(git(folder, "status", "--porcelain", check=False)[1])


def backup(main: Path, doomed: List[Verdict]) -> Path:
    """Write one bundle with every branch about to be deleted and the uncommitted work about to be removed."""
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    folder = common_dir(main) / STATE_FOLDER / BACKUPS
    folder.mkdir(parents=True, exist_ok=True)
    bundle = folder / f"branches-{stamp}.bundle"
    refs: List[str] = []
    saved: List[str] = []
    for number, verdict in enumerate(doomed):
        if verdict.folder is not None:
            commit = snapshot_commit(main, verdict.folder, None, f"Leftover folder {verdict.folder}")
            saved.append(f"{BACKUP_REFS}/{stamp}/{number}-{verdict.name}")
            git(main, "update-ref", saved[-1], commit)
            continue
        refs.append(f"{REMOTE_PREFIX}{verdict.name}" if verdict.remote else f"refs/heads/{verdict.name}")
        if verdict.worktree is not None and verdict.worktree.is_dir() and has_uncommitted_work(verdict.worktree):
            parent = git(verdict.worktree, "rev-parse", "HEAD")[1]
            message = f"Uncommitted work of {verdict.worktree}"
            commit = snapshot_commit(main, verdict.worktree, parent, message)
            saved.append(f"{BACKUP_REFS}/{stamp}/{number}-{verdict.name}")
            git(main, "update-ref", saved[-1], commit)
    try:
        git(main, "bundle", "create", "--quiet", str(bundle), *refs, *saved)
    except Exception as error:
        print(
            f"error: the backup bundle could not be written ({type(error).__name__}): nothing deleted.", file=sys.stderr
        )
        raise
    finally:
        for ref in saved:
            git(main, "update-ref", "-d", ref, check=False)
    return bundle


############
# Clean-up #
############


def clean(main: Path, verdicts: List[Verdict], dry_run: bool) -> List[Verdict]:
    """Delete every merged, integrated or superseded branch and folder, after a backup; return what was deleted."""
    doomed = [verdict for verdict in verdicts if verdict.deletable]
    if not doomed:
        print("🌿 No branch to delete: every branch left has work of its own or is protected.")
        return []
    if dry_run:
        for verdict in doomed:
            print(f"  🧹 would delete {verdict.label} ({verdict.kind})")
        print(f"🌿 Dry run: {len(doomed)} to delete, nothing changed.")
        return doomed
    bundle = backup(main, doomed)
    print(f"💾 Backup: {bundle} ({len(doomed)} branches and folders)")
    for verdict in doomed:
        if verdict.worktree is not None:
            git(main, "worktree", "remove", "--force", str(verdict.worktree), check=False)
    local = [verdict.name for verdict in doomed if not verdict.remote and verdict.folder is None]
    if local:
        git(main, "branch", "-D", *local)
    remote = [verdict.name for verdict in doomed if verdict.remote]
    if remote and has_remote(main):
        code, _ = git(main, "push", "--quiet", REMOTE, "--delete", *remote, check=False)
        if code != 0:
            print(f"note: GitHub kept {', '.join(remote)}: delete them there, or run prune again.", file=sys.stderr)
    for verdict in doomed:
        if verdict.folder is not None:
            shutil.rmtree(verdict.folder)
            if not any(verdict.folder.parent.iterdir()):
                verdict.folder.parent.rmdir()
    git(main, "worktree", "prune", check=False)
    for verdict in doomed:
        print(f"  🧹 {verdict.label} deleted ({verdict.kind})")
    print(f"↩️  Restore any of them with: git fetch {bundle} 'refs/*:refs/restored/*'")
    return doomed
