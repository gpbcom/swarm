#!/usr/bin/env python3
"""Carry the uncommitted work of a ticket between worktrees, and commit it once, when the ticket is done (TKT-5, TKT-16).

Usage (any command but start and handoff may run from the main checkout or from the ticket's worktree):
    python3 .claude/scripts/ticket_tree.py prepare   --ticket T0.07
    python3 .claude/scripts/ticket_tree.py home      --ticket T0.07
    python3 .claude/scripts/ticket_tree.py status    --ticket T0.07
    python3 .claude/scripts/ticket_tree.py start     --ticket T0.07                 (worker worktree, first step)
    python3 .claude/scripts/ticket_tree.py handoff   --ticket T0.07 --task K01      (worker worktree, last step)
    python3 .claude/scripts/ticket_tree.py integrate --ticket T0.07 --task K01 [--task K02 ...] [--resolved]
    python3 .claude/scripts/ticket_tree.py diff      --ticket T0.07 [--from TREE] [--name-only]
    python3 .claude/scripts/ticket_tree.py changes   --ticket T0.07 [--write | --check]
    python3 .claude/scripts/ticket_tree.py docs      --ticket T0.07                 (prints nothing when all is well)
    python3 .claude/scripts/ticket_tree.py finish    --ticket T0.07 [--no-pull-request]

Every ticket lives in its own worktree, its *home*: ``<repository>-tickets/<ID>/`` beside the main checkout, on the
GitFlow branch ``feature/<ID>`` (TKT-15). The main checkout stays on ``develop``, so several tickets run at once
(TKT-16). Nothing is committed before ``finish``: the ticket's work stays uncommitted in its home. Instead of commits,
the script uses git *trees* (``git write-tree`` on a temporary index), which never appear in the history:

- ``prepare`` creates the home from ``origin/develop`` (``develop`` without a remote) and moves the ticket's folder
  ``docs/tickets/<ID>/`` into it from the checkout it runs in. Run again, it keeps the home and its work.
- ``home`` prints the home's path.
- ``start`` copies the home's uncommitted work into a fresh worker worktree, and records the tree it starts from in
  the worktree's git directory (``swarm-base-tree``, also read by ``.claude/hooks/check_touched.py``). A worker created
  from another commit (``develop`` moved since the ticket started) is first moved to the home's commit.
- ``handoff`` saves the worker's own changes, from that tree to its current files, as a patch in
  ``<git common dir>/swarm/<ID>/pending/``. Run it again after any later change.
- ``integrate`` applies the hand-offs to the home in the order given, stops at the first conflict (with ``.rej``
  files to resolve by hand, then ``--resolved``), removes the integrated worktrees, and records the task ids (TKT-11).
  It prints the tree of the integrated work, which ``diff --from`` compares with later.
- ``changes`` writes the table of changed files and line ranges between ``<!-- changes -->`` markers of
  ``EXPLAIN.md`` (TKT-14), leaving out the ticket's own folder. Every file and every line range in it is a link.
- ``docs`` checks ``EXPLAIN.md`` and ``IMPLEMENTATION.md`` (TKT-14): the changes table is up to date, no placeholder
  is left, every file and line mentioned is a clickable relative link, and every link resolves (the file exists, the
  line ``#L<n>`` or range ``#L<a>-L<b>`` is inside it, and a ``path:42`` link text matches its ``#L42``). It prints one
  problem per line, and nothing when all is well. ``finish`` refuses to commit while it finds a problem.
- ``finish`` makes the one commit on ``feature/<ID>``. With a remote ``origin``, it rebases that commit on
  ``origin/develop`` when ``develop`` moved, pushes the branch and opens its pull request to ``develop`` (``Closes #n``,
  label ``automerge``): GitHub merges it once CI passes (TKT-15). Without a remote, it merges the branch into
  ``develop`` in the main checkout with ``--no-ff``. Then it removes the state; the home stays until
  ``tickets.py prune`` finds the branch merged.

Each command prints JSON (or the diff or table asked for) on stdout, and a failure on stderr with exit code 1.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

JsonData = Union[str, int, bool, None, List["JsonData"], Dict[str, "JsonData"]]

TICKET_PATTERN = re.compile(r"^T\d\.\d{2}$")
HUNK_PATTERN = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")
DEVELOP = "develop"
REMOTE = "origin"
BRANCH_PREFIX = "feature/"
LEGACY_PREFIX = "ticket/"
TICKETS_SUFFIX = "-tickets"
AUTOMERGE_LABEL = "automerge"
GITHUB_STATE = ".claude/github.json"
STATE_FOLDER = "swarm"
STATE_FILE = "state.json"
INTEGRATED_PATCH = "integrated.patch"
PENDING = "pending"
APPLIED = "applied"
BASE_TREE_FILE = "swarm-base-tree"
TICKET_FILE = "swarm-ticket"
WORKTREE_BRANCH_PREFIX = "worktree-"
CHANGES_START = "<!-- changes -->"
CHANGES_END = "<!-- /changes -->"
REPO_FROM_TICKET_FOLDER = "../../../"
DOCUMENTS = ("EXPLAIN.md", "IMPLEMENTATION.md")
LINK_PATTERN = re.compile(r"\[((?:[^\[\]]|\[[^\]]*\])*)\]\(([^)\s]+)\)")
CODE_SPAN_PATTERN = re.compile(r"`([^`\n]+)`")
LINE_FRAGMENT_PATTERN = re.compile(r"^L(\d+)(?:-L?(\d+))?$")
PATH_AND_LINE_PATTERN = re.compile(r"^(?P<path>[\w.@/-]+?)(?::(?P<first>\d+)(?:-(?P<last>\d+))?)?$")
PLAIN_PATH_PATTERN = re.compile(r"(?<![\w/.:@-])(?P<path>[\w.@-]+(?:/[\w.@-]+)*\.\w+)(?::(?P<first>\d+))?")
TEXT_LINE_PATTERN = re.compile(r":(\d+)(?:-(\d+))?`?$")
SCHEME_PATTERN = re.compile(r"^[a-z][a-z0-9+.-]*:", re.IGNORECASE)
STATUS_NAMES = {"A": "Added", "M": "Modified", "D": "Deleted", "R": "Renamed", "C": "Copied", "T": "Type changed"}


class TicketTreeError(Exception):
    """Raised when a command cannot do what it was asked, with the reason for the person or the agent."""


###############
# Git helpers #
###############


def git(cwd: Path, *args: str, index: Optional[Path] = None, check: bool = True) -> Tuple[int, str]:
    """Run git in ``cwd`` and return its exit code and standard output, raising on failure when ``check``."""
    env = dict(os.environ)
    if index is not None:
        env["GIT_INDEX_FILE"] = str(index)
    try:
        result = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, env=env, check=False)
    except FileNotFoundError as error:
        raise TicketTreeError("git is not installed.") from error
    if check and result.returncode != 0:
        raise TicketTreeError(f"git {' '.join(args)} failed: {result.stderr.strip() or result.stdout.strip()}")
    return result.returncode, result.stdout.strip()


def top_of(cwd: Path) -> Path:
    """Return the top of the checkout or worktree that holds ``cwd``."""
    return Path(git(cwd, "rev-parse", "--show-toplevel")[1])


def git_dir(top: Path) -> Path:
    """Return the git directory of this checkout or worktree."""
    return Path(git(top, "rev-parse", "--absolute-git-dir")[1]).resolve()


def common_dir(top: Path) -> Path:
    """Return the git directory shared by the main checkout and every worktree."""
    path = Path(git(top, "rev-parse", "--git-common-dir")[1])
    return (path if path.is_absolute() else top / path).resolve()


def is_linked_worktree(top: Path) -> bool:
    """Tell whether ``top`` is a linked worktree rather than the main checkout."""
    return git_dir(top) != common_dir(top)


def main_checkout(top: Path) -> Path:
    """Return the top of the main checkout, the first entry of ``git worktree list``."""
    for line in git(top, "worktree", "list", "--porcelain")[1].splitlines():
        if line.startswith("worktree "):
            return Path(line[len("worktree ") :])
    raise TicketTreeError("git worktree list printed no worktree.")


def head(top: Path) -> str:
    """Return the commit HEAD points at."""
    return git(top, "rev-parse", "HEAD")[1]


def current_branch(top: Path) -> str:
    """Return the checked out branch, or an empty string when HEAD is detached."""
    return git(top, "branch", "--show-current")[1]


def branch_exists(top: Path, branch: str) -> bool:
    """Tell whether a local branch exists."""
    return git(top, "rev-parse", "--verify", "--quiet", f"refs/heads/{branch}", check=False)[0] == 0


def ticket_branch(ticket: str) -> str:
    """Return the GitFlow branch of a ticket (TKT-15)."""
    return f"{BRANCH_PREFIX}{ticket}"


def worktrees(top: Path) -> List[Tuple[Path, str]]:
    """Return every checkout of the repository with its branch (empty when HEAD is detached), main checkout first."""
    found: List[Tuple[Path, str]] = []
    path: Optional[Path] = None
    for line in git(top, "worktree", "list", "--porcelain")[1].splitlines() + [""]:
        if line.startswith("worktree "):
            path = Path(line[len("worktree ") :])
        elif line.startswith("branch ") and path is not None:
            found.append((path, line[len("branch refs/heads/") :]))
            path = None
        elif not line and path is not None:
            found.append((path, ""))
            path = None
    return found


def find_home(top: Path, ticket: str) -> Optional[Path]:
    """Return the checkout on the ticket's branch (or its branch from before TKT-15), if there is one."""
    for path, branch in worktrees(top):
        if branch in (ticket_branch(ticket), f"{LEGACY_PREFIX}{ticket}"):
            return path
    return None


def home_of(top: Path, ticket: str) -> Path:
    """Return the ticket's home, the checkout where its uncommitted work lives (TKT-16)."""
    found = find_home(top, ticket)
    if found is None:
        raise TicketTreeError(f"No checkout holds {ticket_branch(ticket)}: run prepare --ticket {ticket} first.")
    return found


def tickets_root(top: Path) -> Path:
    """Return the folder of the tickets' homes, beside the main checkout."""
    main = main_checkout(top)
    return main.parent / f"{main.name}{TICKETS_SUFFIX}"


def has_remote(top: Path) -> bool:
    """Tell whether the repository has the remote the pull requests go to."""
    return git(top, "remote", "get-url", REMOTE, check=False)[0] == 0


def is_clean(top: Path) -> bool:
    """Tell whether a checkout has no change to its tracked files."""
    return not git(top, "status", "--porcelain", "--untracked-files=no")[1]


def snapshot(top: Path) -> str:
    """Return the tree of every file of the checkout, tracked or not (ignored files excepted), without committing.

    The real index is copied to a temporary one, so ``git add -A`` changes nothing the person or the agent sees.
    """
    real_index = Path(git(top, "rev-parse", "--git-path", "index")[1])
    real_index = real_index if real_index.is_absolute() else top / real_index
    with tempfile.TemporaryDirectory() as folder:
        index = Path(folder) / "index"
        if real_index.is_file():
            shutil.copy2(real_index, index)
        git(top, "add", "-A", index=index)
        return git(top, "write-tree", index=index)[1]


def write_patch(top: Path, base: str, tree: str, path: Path) -> None:
    """Write the binary patch from ``base`` to ``tree`` into ``path``."""
    path.parent.mkdir(parents=True, exist_ok=True)
    git(top, "diff", "--binary", "--full-index", "--no-color", base, tree, f"--output={path}")


def changed_names(top: Path, base: str, tree: str) -> List[str]:
    """Return the paths that differ between ``base`` and ``tree``."""
    return [line for line in git(top, "diff", "--name-only", base, tree)[1].splitlines() if line]


def rejects(top: Path) -> List[str]:
    """Return the ``.rej`` files left by a conflicting patch."""
    others = git(top, "ls-files", "--others", "--exclude-standard")[1].splitlines()
    return [name for name in others if name.endswith(".rej")]


#################
# State helpers #
#################


def ticket_folder(ticket: str) -> str:
    """Return the ticket's folder, relative to the repository root, with a trailing slash."""
    return f"docs/tickets/{ticket}/"


def state_dir(top: Path, ticket: str) -> Path:
    """Return the folder that holds the ticket's hand-offs and state, shared by every worktree."""
    return common_dir(top) / STATE_FOLDER / ticket


def load_state(top: Path, ticket: str) -> Dict[str, JsonData]:
    """Return the ticket's state, or an empty one."""
    path = state_dir(top, ticket) / STATE_FILE
    if path.is_file():
        loaded: Dict[str, JsonData] = json.loads(path.read_text(encoding="utf-8"))
        return loaded
    return {"ticket": ticket, "integrated": [], "tree": ""}


def save_state(top: Path, ticket: str, state: Dict[str, JsonData]) -> None:
    """Write the ticket's state."""
    folder = state_dir(top, ticket)
    folder.mkdir(parents=True, exist_ok=True)
    (folder / STATE_FILE).write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def integrated_ids(state: Dict[str, JsonData]) -> List[str]:
    """Return the integrated task ids, once each, in order."""
    seen: List[str] = []
    for task in state.get("integrated") or []:  # type: ignore[union-attr]
        if isinstance(task, str) and task not in seen:
            seen.append(task)
    return seen


def slug(task: str) -> str:
    """Return a file name for a task id, which may hold a path (``FIX-services/a.py``)."""
    return re.sub(r"[^A-Za-z0-9._-]+", "_", task)


def require_home(top: Path, ticket: str) -> Path:
    """Return the ticket's home, refusing a worker worktree (whose work is handed off, never integrated in place)."""
    if is_worker(top):
        raise TicketTreeError(
            "Run this command in the main checkout or the ticket's worktree, not in a worker worktree."
        )
    return home_of(top, ticket)


def is_worker(top: Path) -> bool:
    """Tell whether ``top`` is a worker worktree of the workflow (a linked worktree on a ``worktree-`` branch)."""
    return is_linked_worktree(top) and current_branch(top).startswith(WORKTREE_BRANCH_PREFIX)


def move_ticket_folder(source: Path, home: Path, ticket: str) -> List[str]:
    """Move the ticket's files that git does not track from ``source`` into the home, and return their paths."""
    folder = ticket_folder(ticket)
    if source.resolve() == home.resolve() or not (source / folder).is_dir():
        return []
    untracked = git(source, "ls-files", "--others", "--exclude-standard", "--", folder)[1].splitlines()
    modified = git(source, "ls-files", "--modified", "--", folder)[1].splitlines()
    moved: List[str] = []
    for name in [*untracked, *modified]:
        target = home / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source / name, target)
        moved.append(name)
    for name in untracked:
        (source / name).unlink()
    for name in modified:
        git(source, "checkout", "--", name)
    leftovers = sorted((source / folder).rglob("*"), reverse=True)
    for path in leftovers:
        if path.is_dir() and not any(path.iterdir()):
            path.rmdir()
    if (source / folder).is_dir() and not any((source / folder).iterdir()):
        (source / folder).rmdir()
    return moved


def remove_worktree(main: Path, meta: Dict[str, JsonData]) -> None:
    """Remove a worker worktree and its harness branch once its hand-off is integrated or obsolete."""
    path = Path(str(meta.get("worktree") or ""))
    if str(path) and path.exists() and path.resolve() != main.resolve():
        code, _ = git(main, "worktree", "remove", "--force", str(path), check=False)
        if code != 0:
            print(f"note: could not remove the worktree {path}.", file=sys.stderr)
    branch = str(meta.get("branch") or "")
    if branch.startswith(WORKTREE_BRANCH_PREFIX) and branch_exists(main, branch):
        git(main, "branch", "-D", branch, check=False)


############
# Commands #
############


def prepare(top: Path, ticket: str) -> Dict[str, JsonData]:
    """Give the ticket its own worktree on ``feature/<ID>``, move its folder into it, and record where it starts."""
    if is_worker(top):
        raise TicketTreeError("Run prepare in the main checkout or the ticket's worktree, not in a worker worktree.")
    home = find_home(top, ticket)
    if home is None:
        if not branch_exists(top, DEVELOP):
            git(top, "branch", DEVELOP)
        start_point = DEVELOP
        if has_remote(top):
            git(top, "fetch", "--quiet", REMOTE, DEVELOP, check=False)
            remote_develop = f"{REMOTE}/{DEVELOP}"
            if git(top, "rev-parse", "--verify", "--quiet", remote_develop, check=False)[0] == 0:
                start_point = remote_develop
        home = tickets_root(top) / ticket
        if home.exists():
            raise TicketTreeError(f"{home} exists but holds no ticket branch: move it away, then run again.")
        home.parent.mkdir(parents=True, exist_ok=True)
        branch = ticket_branch(ticket)
        if branch_exists(top, branch):
            git(top, "worktree", "add", str(home), branch)
        else:
            git(top, "worktree", "add", "--no-track", "-b", branch, str(home), start_point)
    moved = move_ticket_folder(top, home, ticket)
    state = load_state(home, ticket)
    if not state.get("base") or not moved:
        state["base"] = head(home)
    state["tree"] = snapshot(home)
    state["home"] = str(home)
    save_state(home, ticket, state)
    write_patch(home, str(state["base"]), str(state["tree"]), state_dir(home, ticket) / INTEGRATED_PATCH)
    return {
        "branch": current_branch(home),
        "home": str(home),
        "base": state["base"],
        "tree": state["tree"],
        "moved": list(moved),
        "integrated": integrated_ids(state),
    }


def status(top: Path, ticket: str) -> Dict[str, JsonData]:
    """Return the integrated task ids and the last integrated tree.

    A ticket started before TKT-5 dropped intermediate commits has one commit per task (``<ID> K01: ...``) on its
    branch: those tasks count as integrated too, so that its re-run still continues where it stopped (TKT-11).
    """
    state = load_state(top, ticket)
    integrated = integrated_ids(state)
    branch = f"{LEGACY_PREFIX}{ticket}"
    if branch_exists(top, branch) and branch_exists(top, DEVELOP):
        subjects = git(top, "log", f"{DEVELOP}..{branch}", "--format=%s")[1].splitlines()
        pattern = re.compile(rf"^{re.escape(ticket)} (K\d{{2}}):")
        committed = [found.group(1) for found in map(pattern.match, reversed(subjects)) if found]
        integrated = [*[task for task in dict.fromkeys(committed) if task not in integrated], *integrated]
    return {"ticket": ticket, "integrated": integrated, "tree": state.get("tree") or ""}


def start(top: Path, ticket: str) -> Dict[str, JsonData]:
    """Copy the home's uncommitted work into this worker worktree and record the tree it starts from."""
    if not is_linked_worktree(top) or find_home(top, ticket) == top:
        raise TicketTreeError("Run start in a worker worktree, not in the main checkout or the ticket's worktree.")
    folder = git_dir(top)
    marker = folder / BASE_TREE_FILE
    if marker.is_file() and (folder / TICKET_FILE).read_text(encoding="utf-8").strip() == ticket:
        return {"started": False, "base_tree": marker.read_text(encoding="utf-8").strip(), "note": "already started"}
    home = home_of(top, ticket)
    if snapshot(top) != git(top, "rev-parse", "HEAD^{tree}")[1]:
        raise TicketTreeError("This worktree already has changes: run start before changing anything.")
    moved_from = ""
    if head(top) != head(home):
        moved_from = head(top)
        git(top, "reset", "--hard", "--quiet", head(home))
    home_tree = snapshot(home)
    with tempfile.TemporaryDirectory() as temporary:
        patch = Path(temporary) / "start.patch"
        write_patch(home, head(home), home_tree, patch)
        if patch.stat().st_size:
            git(top, "apply", "--binary", "--whitespace=nowarn", str(patch))
    base_tree = snapshot(top)
    if base_tree != home_tree:
        raise TicketTreeError("The copy of the ticket's work differs from it: check .gitignore and file modes.")
    marker.write_text(base_tree + "\n", encoding="utf-8")
    (folder / TICKET_FILE).write_text(ticket + "\n", encoding="utf-8")
    result: Dict[str, JsonData] = {"started": True, "base_tree": base_tree, "home": str(home)}
    result["files"] = len(changed_names(top, "HEAD", base_tree))
    if moved_from:
        result["moved_from"] = moved_from
    return result


def handoff(top: Path, ticket: str, task: str) -> Dict[str, JsonData]:
    """Save this worker's own changes as a patch for the integrator."""
    marker = git_dir(top) / BASE_TREE_FILE
    if not is_linked_worktree(top) or not marker.is_file():
        raise TicketTreeError("Run handoff in a worker worktree after start.")
    base_tree = marker.read_text(encoding="utf-8").strip()
    tree = snapshot(top)
    pending = state_dir(top, ticket) / PENDING
    write_patch(top, base_tree, tree, pending / f"{slug(task)}.patch")
    files = git(top, "diff", "--name-status", base_tree, tree)[1].splitlines()
    meta: Dict[str, JsonData] = {
        "task": task,
        "worktree": str(top),
        "branch": current_branch(top),
        "base_tree": base_tree,
        "tree": tree,
        "files": [line for line in files if line],
    }
    (pending / f"{slug(task)}.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    return meta


def integrate(top: Path, ticket: str, tasks: List[str], resolved: bool) -> Tuple[Dict[str, JsonData], int]:
    """Apply the hand-offs of ``tasks`` to the ticket's home, in order, stopping at the first conflict."""
    top = require_home(top, ticket)
    left = rejects(top)
    if left:
        raise TicketTreeError(f"Resolve and delete these .rej files first: {', '.join(left)}.")
    folder = state_dir(top, ticket)
    state = load_state(top, ticket)
    done: List[JsonData] = []
    conflicts: List[JsonData] = []
    remaining = list(tasks)
    while remaining:
        task = remaining[0]
        patch = folder / PENDING / f"{slug(task)}.patch"
        meta_path = patch.with_suffix(".json")
        if not patch.is_file():
            raise TicketTreeError(f"No hand-off for {task}: the worker must run handoff --task {task}.")
        if not resolved and patch.stat().st_size:
            code, _ = git(top, "apply", "--check", "--binary", "--whitespace=nowarn", str(patch), check=False)
            if code != 0:
                git(top, "apply", "--binary", "--whitespace=nowarn", "--reject", str(patch), check=False)
                conflicts.append({"task": task, "rejects": rejects(top), "patch": str(patch)})
                break
            git(top, "apply", "--binary", "--whitespace=nowarn", str(patch))
        meta: Dict[str, JsonData] = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.is_file() else {}
        applied = folder / APPLIED
        applied.mkdir(parents=True, exist_ok=True)
        number = len(list(applied.glob("*.patch"))) + 1
        patch.replace(applied / f"{number:03d}-{slug(task)}.patch")
        if meta_path.is_file():
            meta_path.replace(applied / f"{number:03d}-{slug(task)}.json")
        integrated = state.get("integrated")
        state["integrated"] = [*(integrated if isinstance(integrated, list) else []), task]
        remove_worktree(top, meta)
        done.append(task)
        remaining.pop(0)
    if not conflicts:
        state["base"] = head(top)
        state["tree"] = snapshot(top)
        write_patch(top, str(state["base"]), str(state["tree"]), folder / INTEGRATED_PATCH)
    save_state(top, ticket, state)
    result: Dict[str, JsonData] = {
        "integrated": done,
        "conflicts": conflicts,
        "remaining": remaining,
        "tree": state.get("tree") or "",
    }
    return result, 1 if conflicts else 0


def diff(top: Path, ticket: str, from_tree: Optional[str], name_only: bool) -> str:
    """Return the diff of the ticket's uncommitted work, from HEAD or from an earlier integrated tree."""
    top = require_home(top, ticket)
    base = from_tree or head(top)
    options = ["--name-status"] if name_only else ["--no-color"]
    return git(top, "diff", *options, base, snapshot(top))[1]


def line_ranges(numbers: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
    """Merge (first, last) line ranges that touch or overlap."""
    merged: List[Tuple[int, int]] = []
    for first, last in sorted(numbers):
        if merged and first <= merged[-1][1] + 1:
            merged[-1] = (merged[-1][0], max(merged[-1][1], last))
        else:
            merged.append((first, last))
    return merged


def changes_table(top: Path, ticket: str) -> str:
    """Return the Markdown table of the files the ticket changes, with the line ranges in their new version."""
    tree = snapshot(top)
    excluded = f":(exclude){ticket_folder(ticket)}"
    statuses: Dict[str, str] = {}
    for line in git(top, "diff", "--name-status", "-M", head(top), tree, "--", ".", excluded)[1].splitlines():
        parts = line.split("\t")
        if len(parts) >= 2:
            code = parts[0][:1]
            name = STATUS_NAMES.get(code, code)
            statuses[parts[-1]] = f"{name} from `{parts[1]}`" if code in "RC" and len(parts) == 3 else name
    counts: Dict[str, Tuple[str, str]] = {}
    for line in git(top, "diff", "--numstat", "-M", head(top), tree, "--", ".", excluded)[1].splitlines():
        parts = line.split("\t")
        if len(parts) == 3:
            path = parts[2]
            if " => " in path:
                path = statuses_key(path, statuses)
            counts[path] = (parts[0], parts[1])
    ranges: Dict[str, List[Tuple[int, int]]] = {}
    removed_only: Dict[str, List[int]] = {}
    current = ""
    for line in git(top, "diff", "-U0", "-M", "--no-color", head(top), tree, "--", ".", excluded)[1].splitlines():
        if line.startswith("+++ "):
            current = line[6:] if line.startswith("+++ b/") else ""
            continue
        found = HUNK_PATTERN.match(line)
        if found and current:
            start_line = int(found.group(3))
            length = int(found.group(4)) if found.group(4) is not None else 1
            if length:
                ranges.setdefault(current, []).append((start_line, start_line + length - 1))
            else:
                removed_only.setdefault(current, []).append(start_line)
    rows = ["| File | Change | Lines in the new version | Added | Removed |", "| --- | --- | --- | --- | --- |"]
    total_added = 0
    total_removed = 0
    for path in sorted(statuses):
        added, removed = counts.get(path, ("-", "-"))
        total_added += int(added) if added.isdigit() else 0
        total_removed += int(removed) if removed.isdigit() else 0
        link = f"{REPO_FROM_TICKET_FOLDER}{path}"
        if statuses[path] == STATUS_NAMES["D"]:
            file_cell, lines = f"`{path}`", "➖ deleted"
        elif added == "-":
            file_cell, lines = f"[`{path}`]({link})", "binary"
        else:
            file_cell = f"[`{path}`]({link})"
            spans = [
                f"[{a}]({link}#L{a})" if a == b else f"[{a}-{b}]({link}#L{a})"
                for a, b in line_ranges(ranges.get(path, []))
            ]
            spans += [
                f"[removed after {n}]({link}#L{n})" if n else f"[removed at the top]({link}#L1)"
                for n in removed_only.get(path, [])
            ]
            lines = ", ".join(spans) or "➖"
        rows.append(f"| {file_cell} | {statuses[path]} | {lines} | +{added} | −{removed} |")
    rows.append(f"| **{len(statuses)} files** | | | **+{total_added}** | **−{total_removed}** |")
    return "\n".join(rows)


def statuses_key(numstat_path: str, statuses: Dict[str, str]) -> str:
    """Return the new path of a renamed file as ``--numstat`` writes it (``a/{x => y}/b`` or ``x => y``)."""
    braces = re.match(r"^(.*)\{(.*) => (.*)\}(.*)$", numstat_path)
    if braces:
        candidate = f"{braces.group(1)}{braces.group(3)}{braces.group(4)}".replace("//", "/")
    else:
        candidate = numstat_path.split(" => ", 1)[1]
    return candidate if candidate in statuses else numstat_path


def changes(top: Path, ticket: str, mode: str) -> Tuple[str, int]:
    """Print, write or check the changes table of ``EXPLAIN.md``."""
    top = require_home(top, ticket)
    table = changes_table(top, ticket)
    if mode == "print":
        return table, 0
    path = top / ticket_folder(ticket) / "EXPLAIN.md"
    text = path.read_text(encoding="utf-8") if path.is_file() else ""
    if CHANGES_START not in text or CHANGES_END not in text:
        raise TicketTreeError(f"{path.name} has no {CHANGES_START} ... {CHANGES_END} markers.")
    before, rest = text.split(CHANGES_START, 1)
    _, after = rest.split(CHANGES_END, 1)
    wanted = f"{before}{CHANGES_START}\n{table}\n{CHANGES_END}{after}"
    if mode == "check":
        if text != wanted:
            return f"{ticket_folder(ticket)}EXPLAIN.md: the changes table is out of date. Run changes --write.", 1
        return "", 0
    path.write_text(wanted, encoding="utf-8")
    return "", 0


def strip_non_prose(text: str) -> str:
    """Return the text without HTML comments and fenced code blocks, where paths are commands, not references."""
    text = re.sub(r"<!--.*?-->", " ", text, flags=re.DOTALL)
    return re.sub(r"^```.*?^```", " ", text, flags=re.DOTALL | re.MULTILINE)


def line_count(path: Path) -> int:
    """Return the number of lines of a text file."""
    return len(path.read_text(encoding="utf-8", errors="replace").splitlines())


def link_problems(top: Path, folder: Path, name: str, text: str, target: str) -> List[str]:
    """Return what is wrong with one link of a ticket document: a missing file, a line outside it, a wrong line."""
    if SCHEME_PATTERN.match(target) or target.startswith("#"):
        return []
    file_part, _, fragment = target.partition("#")
    resolved = (folder / file_part).resolve()
    if not resolved.exists():
        return [f"{name}: the link ({target}) points at a file that does not exist."]
    if not fragment or resolved.suffix == ".md" or resolved.is_dir():
        return []
    found = LINE_FRAGMENT_PATTERN.match(fragment)
    if found is None:
        return [f"{name}: the link ({target}) must point at a line, as #L42 or #L42-L50."]
    first = int(found.group(1))
    last = int(found.group(2) or first)
    count = max(line_count(resolved), 1)
    if not 1 <= first <= last <= count:
        return [f"{name}: the link ({target}) points outside {file_part.split('/')[-1]}, which has {count} lines."]
    named = TEXT_LINE_PATTERN.search(text.strip())
    if named and int(named.group(1)) != first:
        return [f"{name}: the link text {text} names line {named.group(1)} but the link opens line {first}."]
    return []


def is_known_file(top: Path, folder: Path, candidate: str) -> bool:
    """Tell whether ``candidate`` names a file of the repository or of the ticket's folder."""
    return bool(candidate) and ((top / candidate).is_file() or (folder / candidate).is_file())


def document_problems(top: Path, ticket: str) -> List[str]:
    """Return every problem of ``EXPLAIN.md`` and ``IMPLEMENTATION.md``, one sentence each (TKT-14)."""
    top = require_home(top, ticket)
    folder = top / ticket_folder(ticket)
    problems: List[str] = []
    try:
        message, code = changes(top, ticket, "check")
        if code:
            problems.append(message)
    except TicketTreeError as error:
        problems.append(f"EXPLAIN.md: {error}")
    for name in DOCUMENTS:
        path = folder / name
        if not path.is_file():
            problems.append(f"{name}: missing.")
            continue
        prose = strip_non_prose(path.read_text(encoding="utf-8"))
        if "{{" in prose:
            problems.append(f"{name}: a {{{{...}}}} placeholder of the template is left.")
        for found in LINK_PATTERN.finditer(prose):
            problems.extend(link_problems(top, folder, name, found.group(1), found.group(2)))
        outside_links = LINK_PATTERN.sub(" ", prose)
        for span in CODE_SPAN_PATTERN.finditer(outside_links):
            found = PATH_AND_LINE_PATTERN.match(span.group(1).strip())
            if found and is_known_file(top, folder, found.group("path")):
                problems.append(
                    f"{name}: `{span.group(1)}` is not clickable. Write it as a link, such as "
                    f"[`{span.group(1)}`]({REPO_FROM_TICKET_FOLDER}{found.group('path')}"
                    f"{'#L' + found.group('first') if found.group('first') else ''})."
                )
        for found in PLAIN_PATH_PATTERN.finditer(CODE_SPAN_PATTERN.sub(" ", outside_links)):
            if is_known_file(top, folder, found.group("path")) and ("/" in found.group("path") or found.group("first")):
                problems.append(f"{name}: {found.group(0)} is not clickable. Write it as a link to the file and line.")
    return problems


def documents(top: Path, ticket: str) -> Tuple[str, int]:
    """Check the ticket's documents, returning the problems one per line and 1 when there is any."""
    problems = document_problems(top, ticket)
    return "\n".join(problems), 1 if problems else 0


def ticket_title(home: Path, ticket: str) -> str:
    """Return the title of ``TICKET.md`` (``T0.07: Rust core and benchmark gate``), or the ticket ID."""
    ticket_md = home / ticket_folder(ticket) / "TICKET.md"
    if ticket_md.is_file():
        for line in ticket_md.read_text(encoding="utf-8").splitlines():
            if line.startswith("# "):
                return line[2:].strip() or ticket
    return ticket


def issue_number(top: Path, ticket: str) -> Optional[int]:
    """Return the GitHub issue of the ticket, from ``.claude/github.json`` (written by ``board.py bootstrap``)."""
    for checkout in (top, main_checkout(top)):
        path = checkout / GITHUB_STATE
        if path.is_file():
            issue = json.loads(path.read_text(encoding="utf-8")).get("issues", {}).get(ticket, {})
            if isinstance(issue, dict) and isinstance(issue.get("number"), int):
                return int(issue["number"])
    return None


def run_tool(cwd: Path, *args: str) -> Tuple[int, str]:
    """Run a command other than git (``gh``, a sibling script) and return its exit code and output."""
    try:
        result = subprocess.run(list(args), cwd=cwd, capture_output=True, text=True, check=False)
    except FileNotFoundError:
        return 127, f"{args[0]} is not installed."
    return result.returncode, (result.stdout.strip() or result.stderr.strip())


def pull_request(home: Path, ticket: str, title: str, tasks: List[str]) -> str:
    """Open (or find) the ticket's pull request to ``develop``, labelled for the merge once CI passes."""
    branch = ticket_branch(ticket)
    code, url = run_tool(home, "gh", "pr", "view", branch, "--json", "url", "--jq", ".url")
    if code == 0 and url:
        return url
    issue = issue_number(home, ticket)
    folder = ticket_folder(ticket)
    body = "\n".join(
        [
            f"Closes #{issue}" if issue else f"Roadmap ticket {ticket}.",
            "",
            (
                f"One commit for the whole ticket (TKT-5), worked by the harness in {len(tasks)} tasks: "
                f"{', '.join(tasks) or 'none recorded'}."
            ),
            "",
            f"- 📖 How it works: [{folder}EXPLAIN.md]({folder}EXPLAIN.md)",
            f"- ⚖️ Why this way: [{folder}IMPLEMENTATION.md]({folder}IMPLEMENTATION.md)",
            f"- 👀 Review note: [{folder}REVIEW.md]({folder}REVIEW.md)",
            f"- ⏱️ Progress and tokens: [{folder}PROGRESS.md]({folder}PROGRESS.md)",
            "",
            "Merged into `develop` by the `automerge` workflow once the `ci` checks pass (TKT-15).",
        ]
    )
    run_tool(
        home,
        "gh",
        "label",
        "create",
        AUTOMERGE_LABEL,
        "--color",
        "0e8a16",
        "--force",
        "--description",
        "Merged into develop once CI passes",
    )
    code, url = run_tool(
        home,
        "gh",
        "pr",
        "create",
        "--base",
        DEVELOP,
        "--head",
        branch,
        "--title",
        title,
        "--body",
        body,
        "--label",
        AUTOMERGE_LABEL,
    )
    if code != 0:
        raise TicketTreeError(f"The branch is pushed but the pull request could not be opened: {url}")
    return url.splitlines()[-1]


def publish(home: Path, ticket: str, title: str, tasks: List[str], open_pull_request: bool) -> Dict[str, JsonData]:
    """Rebase the ticket's commit on ``origin/develop`` when needed, push it, and open its pull request."""
    branch = ticket_branch(ticket)
    git(home, "fetch", "--quiet", REMOTE, DEVELOP, check=False)
    remote_develop = f"{REMOTE}/{DEVELOP}"
    rebased = False
    known = git(home, "rev-parse", "--verify", "--quiet", remote_develop, check=False)[0] == 0
    if known and git(home, "merge-base", "--is-ancestor", remote_develop, "HEAD", check=False)[0] != 0:
        code, _ = git(home, "rebase", remote_develop, check=False)
        if code != 0:
            git(home, "rebase", "--abort", check=False)
            raise TicketTreeError(
                f"{branch} does not rebase cleanly on {remote_develop}: another ticket changed the same lines. "
                f"The ticket is committed in {home}: rebase it by hand, then run finish again."
            )
        rebased = True
    code, output = git(home, "push", "--quiet", "--set-upstream", REMOTE, branch, check=False)
    if code != 0:
        code, output = git(home, "push", "--quiet", "--force-with-lease", "--set-upstream", REMOTE, branch, check=False)
    if code != 0:
        raise TicketTreeError(f"git push {REMOTE} {branch} failed: {output}")
    result: Dict[str, JsonData] = {"pushed": True, "rebased": rebased, "branch": branch}
    if open_pull_request:
        result["pull_request"] = pull_request(home, ticket, title, tasks)
        board = home / ".claude" / "scripts" / "board.py"
        if board.is_file():
            run_tool(home, sys.executable, str(board), "move", "--ticket", ticket, "--status", "review")
    return result


def merge_locally(home: Path, ticket: str) -> str:
    """Merge the ticket's branch into ``develop`` in the main checkout with ``--no-ff`` (no remote to open a PR on)."""
    main = main_checkout(home)
    if current_branch(main) != DEVELOP or not is_clean(main):
        raise TicketTreeError(
            f"The ticket is committed on {ticket_branch(ticket)}, but the main checkout is not a clean {DEVELOP}: "
            f"merge it by hand."
        )
    code, output = git(
        main,
        "merge",
        "--no-ff",
        ticket_branch(ticket),
        "-m",
        f"{ticket}: merge {ticket_branch(ticket)} into {DEVELOP}",
        check=False,
    )
    if code != 0:
        git(main, "merge", "--abort", check=False)
        raise TicketTreeError(f"{DEVELOP} does not merge {ticket_branch(ticket)} cleanly: {output}")
    return head(main)


def finish(top: Path, ticket: str, open_pull_request: bool = True) -> Dict[str, JsonData]:
    """Make the ticket's single commit on ``feature/<ID>``, then publish it (TKT-15) or merge it locally."""
    home = require_home(top, ticket)
    left = rejects(home)
    if left:
        raise TicketTreeError(f"Resolve and delete these .rej files first: {', '.join(left)}.")
    if snapshot(home) == git(home, "rev-parse", "HEAD^{tree}")[1]:
        raise TicketTreeError("There is nothing to commit for this ticket.")
    problems = document_problems(home, ticket)
    if problems:
        raise TicketTreeError("Fix the ticket's documents before its commit (TKT-14):\n" + "\n".join(problems))
    state = load_state(home, ticket)
    title = ticket_title(home, ticket)
    tasks = integrated_ids(state)
    git(home, "add", "-A")
    git(home, "commit", "--quiet", "-m", title, "-m", f"Tasks: {', '.join(tasks) or 'none recorded'}.")
    result: Dict[str, JsonData] = {"commit": head(home), "home": str(home), "tasks": list(tasks)}
    if has_remote(home):
        result.update(publish(home, ticket, title, tasks, open_pull_request))
        result["commit"] = head(home)
    else:
        result.update({"pushed": False, "merge": merge_locally(home, ticket), "branch": DEVELOP})
    folder = state_dir(home, ticket)
    for meta_path in sorted((folder / PENDING).glob("*.json")) if (folder / PENDING).is_dir() else []:
        remove_worktree(home, json.loads(meta_path.read_text(encoding="utf-8")))
    shutil.rmtree(folder, ignore_errors=True)
    return result


########
# Main #
########


def parser() -> argparse.ArgumentParser:
    """Return the command line parser."""
    root = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = root.add_subparsers(dest="command", required=True)
    for name in ("prepare", "home", "status", "start", "handoff", "integrate", "diff", "changes", "docs", "finish"):
        command = commands.add_parser(name)
        command.add_argument("--ticket", required=True)
        if name in ("handoff", "integrate"):
            command.add_argument("--task", action="append", required=True)
        if name == "integrate":
            command.add_argument("--resolved", action="store_true")
        if name == "diff":
            command.add_argument("--from", dest="from_tree")
            command.add_argument("--name-only", action="store_true")
        if name == "finish":
            command.add_argument("--no-pull-request", action="store_true")
        if name == "changes":
            mode = command.add_mutually_exclusive_group()
            mode.add_argument("--write", action="store_true")
            mode.add_argument("--check", action="store_true")
    return root


def main() -> int:
    """Run one command and return its exit code."""
    args = parser().parse_args()
    if not TICKET_PATTERN.match(args.ticket):
        print(f"Invalid ticket: {args.ticket!r}. Must look like T0.07.", file=sys.stderr)
        return 2
    try:
        top = top_of(Path.cwd())
        code = 0
        output: Union[str, Dict[str, JsonData]]
        if args.command == "prepare":
            output = prepare(top, args.ticket)
        elif args.command == "home":
            output = {"home": str(home_of(top, args.ticket))}
        elif args.command == "status":
            output = status(top, args.ticket)
        elif args.command == "start":
            output = start(top, args.ticket)
        elif args.command == "handoff":
            output = handoff(top, args.ticket, args.task[-1])
        elif args.command == "integrate":
            output, code = integrate(top, args.ticket, args.task, args.resolved)
        elif args.command == "diff":
            output = diff(top, args.ticket, args.from_tree, args.name_only)
        elif args.command == "changes":
            output, code = changes(top, args.ticket, "write" if args.write else "check" if args.check else "print")
        elif args.command == "docs":
            output, code = documents(top, args.ticket)
        else:
            output = finish(top, args.ticket, not args.no_pull_request)
    except TicketTreeError as error:
        print(f"❌ {error}", file=sys.stderr)
        return 1
    text = output if isinstance(output, str) else json.dumps(output)
    if text:
        print(text)
    return code


if __name__ == "__main__":
    sys.exit(main())
