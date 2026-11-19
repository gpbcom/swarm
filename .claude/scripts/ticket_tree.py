#!/usr/bin/env python3
"""Carry the uncommitted work of a ticket between worktrees, and commit it once, when the ticket is done (TKT-5).

Usage:
    python3 .claude/scripts/ticket_tree.py prepare   --ticket T0.07                 (main checkout)
    python3 .claude/scripts/ticket_tree.py status    --ticket T0.07
    python3 .claude/scripts/ticket_tree.py start     --ticket T0.07                 (worker worktree, first step)
    python3 .claude/scripts/ticket_tree.py handoff   --ticket T0.07 --task K01      (worker worktree, last step)
    python3 .claude/scripts/ticket_tree.py integrate --ticket T0.07 --task K01 [--task K02 ...] [--resolved]
    python3 .claude/scripts/ticket_tree.py diff      --ticket T0.07 [--from TREE] [--name-only]
    python3 .claude/scripts/ticket_tree.py changes   --ticket T0.07 [--write | --check]
    python3 .claude/scripts/ticket_tree.py docs      --ticket T0.07                 (prints nothing when all is well)
    python3 .claude/scripts/ticket_tree.py finish    --ticket T0.07                 (main checkout)

Nothing is committed before ``finish``. The work of the ticket lives, uncommitted, in the main checkout on
``ticket/<ID>``. Instead of commits, the script uses git *trees* (``git write-tree`` on a temporary index), which never
appear in the history:

- ``prepare`` puts the main checkout on ``ticket/<ID>`` (from ``develop``) and refuses changes outside
  ``docs/tickets/<ID>/``, which the single commit would otherwise take.
- ``start`` copies the main checkout's uncommitted work into a fresh worker worktree, and records the tree it starts
  from in the worktree's git directory (``swarm-base-tree``, also read by ``.claude/hooks/check_touched.py``).
- ``handoff`` saves the worker's own changes, from that tree to its current files, as a patch in
  ``<git common dir>/swarm/<ID>/pending/``. Run it again after any later change.
- ``integrate`` applies the hand-offs to the main checkout in the order given, stops at the first conflict (with
  ``.rej`` files to resolve by hand, then ``--resolved``), removes the integrated worktrees, and records the task ids
  (TKT-11). It prints the tree of the integrated work, which ``diff --from`` compares with later.
- ``changes`` writes the table of changed files and line ranges between ``<!-- changes -->`` markers of
  ``EXPLAIN.md`` (TKT-14), leaving out the ticket's own folder. Every file and every line range in it is a link.
- ``docs`` checks ``EXPLAIN.md`` and ``IMPLEMENTATION.md`` (TKT-14): the changes table is up to date, no placeholder
  is left, every file and line mentioned is a clickable relative link, and every link resolves (the file exists, the
  line ``#L<n>`` or range ``#L<a>-L<b>`` is inside it, and a ``path:42`` link text matches its ``#L42``). It prints one
  problem per line, and nothing when all is well. ``finish`` refuses to commit while it finds a problem.
- ``finish`` makes the one commit on ``ticket/<ID>``, merges it into ``develop`` with ``--no-ff``, and removes the
  state. Nothing is pushed.

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


def require_main_on_ticket(top: Path, ticket: str) -> None:
    """Refuse to go on unless ``top`` is the main checkout on ``ticket/<ID>``."""
    if is_linked_worktree(top):
        raise TicketTreeError("Run this command in the main checkout, not in a worker worktree.")
    branch = current_branch(top)
    if branch != f"ticket/{ticket}":
        raise TicketTreeError(f"The main checkout is on {branch or 'a detached HEAD'}, not on ticket/{ticket}.")


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
    """Put the main checkout on ``ticket/<ID>`` and record where the ticket starts."""
    if is_linked_worktree(top):
        raise TicketTreeError("Run prepare in the main checkout, not in a worker worktree.")
    branch = f"ticket/{ticket}"
    if current_branch(top) != branch:
        outside = [
            name for name in changed_names(top, "HEAD", snapshot(top)) if not name.startswith(ticket_folder(ticket))
        ]
        if outside:
            raise TicketTreeError(
                f"The main checkout has changes outside {ticket_folder(ticket)}, which the ticket's single commit "
                f"would take: {', '.join(outside[:20])}. Commit, stash or ignore them, then run again."
            )
        if not branch_exists(top, DEVELOP):
            git(top, "branch", DEVELOP)
        if branch_exists(top, branch):
            git(top, "checkout", branch)
        else:
            git(top, "checkout", "-b", branch, DEVELOP)
    state = load_state(top, ticket)
    state["base"] = head(top)
    state["tree"] = snapshot(top)
    save_state(top, ticket, state)
    write_patch(top, str(state["base"]), str(state["tree"]), state_dir(top, ticket) / INTEGRATED_PATCH)
    return {"branch": branch, "base": state["base"], "tree": state["tree"], "integrated": integrated_ids(state)}


def status(top: Path, ticket: str) -> Dict[str, JsonData]:
    """Return the integrated task ids and the last integrated tree.

    A ticket started before TKT-5 dropped intermediate commits has one commit per task (``<ID> K01: ...``) on its
    branch: those tasks count as integrated too, so that its re-run still continues where it stopped (TKT-11).
    """
    state = load_state(top, ticket)
    integrated = integrated_ids(state)
    branch = f"ticket/{ticket}"
    if branch_exists(top, branch) and branch_exists(top, DEVELOP):
        subjects = git(top, "log", f"{DEVELOP}..{branch}", "--format=%s")[1].splitlines()
        pattern = re.compile(rf"^{re.escape(ticket)} (K\d{{2}}):")
        committed = [found.group(1) for found in map(pattern.match, reversed(subjects)) if found]
        integrated = [*[task for task in dict.fromkeys(committed) if task not in integrated], *integrated]
    return {"ticket": ticket, "integrated": integrated, "tree": state.get("tree") or ""}


def start(top: Path, ticket: str) -> Dict[str, JsonData]:
    """Copy the main checkout's uncommitted work into this worker worktree and record the tree it starts from."""
    if not is_linked_worktree(top):
        raise TicketTreeError("Run start in a worker worktree, not in the main checkout.")
    folder = git_dir(top)
    marker = folder / BASE_TREE_FILE
    if marker.is_file() and (folder / TICKET_FILE).read_text(encoding="utf-8").strip() == ticket:
        return {"started": False, "base_tree": marker.read_text(encoding="utf-8").strip(), "note": "already started"}
    main = main_checkout(top)
    if head(top) != head(main):
        raise TicketTreeError(f"This worktree starts at {head(top)[:9]} but the main checkout is at {head(main)[:9]}.")
    if snapshot(top) != git(top, "rev-parse", "HEAD^{tree}")[1]:
        raise TicketTreeError("This worktree already has changes: run start before changing anything.")
    main_tree = snapshot(main)
    with tempfile.TemporaryDirectory() as temporary:
        patch = Path(temporary) / "start.patch"
        write_patch(main, head(main), main_tree, patch)
        if patch.stat().st_size:
            git(top, "apply", "--binary", "--whitespace=nowarn", str(patch))
    base_tree = snapshot(top)
    if base_tree != main_tree:
        raise TicketTreeError("The copy of the main checkout's work differs from it: check .gitignore and file modes.")
    marker.write_text(base_tree + "\n", encoding="utf-8")
    (folder / TICKET_FILE).write_text(ticket + "\n", encoding="utf-8")
    return {"started": True, "base_tree": base_tree, "files": len(changed_names(top, "HEAD", base_tree))}


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
    """Apply the hand-offs of ``tasks`` to the main checkout, in order, stopping at the first conflict."""
    require_main_on_ticket(top, ticket)
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


def finish(top: Path, ticket: str) -> Dict[str, JsonData]:
    """Make the ticket's single commit, merge it into ``develop`` with ``--no-ff``, and clear the state."""
    require_main_on_ticket(top, ticket)
    left = rejects(top)
    if left:
        raise TicketTreeError(f"Resolve and delete these .rej files first: {', '.join(left)}.")
    if snapshot(top) == git(top, "rev-parse", "HEAD^{tree}")[1]:
        raise TicketTreeError("There is nothing to commit for this ticket.")
    problems = document_problems(top, ticket)
    if problems:
        raise TicketTreeError("Fix the ticket's documents before its commit (TKT-14):\n" + "\n".join(problems))
    state = load_state(top, ticket)
    ticket_md = top / ticket_folder(ticket) / "TICKET.md"
    title = ticket
    if ticket_md.is_file():
        heading = next(
            (line[2:].strip() for line in ticket_md.read_text(encoding="utf-8").splitlines() if line.startswith("# ")),
            "",
        )
        title = heading or ticket
    tasks = integrated_ids(state)
    git(top, "add", "-A")
    git(top, "commit", "-m", title, "-m", f"Tasks: {', '.join(tasks) or 'none recorded'}.")
    commit = head(top)
    git(top, "checkout", DEVELOP)
    code, _ = git(
        top, "merge", "--no-ff", f"ticket/{ticket}", "-m", f"{ticket}: merge ticket/{ticket} into develop", check=False
    )
    if code != 0:
        git(top, "merge", "--abort", check=False)
        git(top, "checkout", f"ticket/{ticket}")
        raise TicketTreeError(
            f"develop does not merge ticket/{ticket} cleanly: the ticket is committed, merge it by hand."
        )
    merge = head(top)
    folder = state_dir(top, ticket)
    for meta_path in sorted((folder / PENDING).glob("*.json")) if (folder / PENDING).is_dir() else []:
        remove_worktree(top, json.loads(meta_path.read_text(encoding="utf-8")))
    shutil.rmtree(folder, ignore_errors=True)
    return {"commit": commit, "merge": merge, "branch": DEVELOP, "tasks": tasks}


########
# Main #
########


def parser() -> argparse.ArgumentParser:
    """Return the command line parser."""
    root = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = root.add_subparsers(dest="command", required=True)
    for name in ("prepare", "status", "start", "handoff", "integrate", "diff", "changes", "docs", "finish"):
        command = commands.add_parser(name)
        command.add_argument("--ticket", required=True)
        if name in ("handoff", "integrate"):
            command.add_argument("--task", action="append", required=True)
        if name == "integrate":
            command.add_argument("--resolved", action="store_true")
        if name == "diff":
            command.add_argument("--from", dest="from_tree")
            command.add_argument("--name-only", action="store_true")
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
            output = finish(top, args.ticket)
    except TicketTreeError as error:
        print(f"❌ {error}", file=sys.stderr)
        return 1
    text = output if isinstance(output, str) else json.dumps(output)
    if text:
        print(text)
    return code


if __name__ == "__main__":
    sys.exit(main())
