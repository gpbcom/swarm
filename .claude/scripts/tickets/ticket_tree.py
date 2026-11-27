#!/usr/bin/env python3
from __future__ import annotations

import argparse
import fcntl
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

USAGE = """Carry the uncommitted work of a ticket between worktrees, and commit it once, when the ticket is done (TKT-5, TKT-16).

Usage (any command but start and handoff may run from the main checkout or from the ticket's worktree):
    python3 .claude/scripts/tickets/ticket_tree.py prepare   --ticket T0.07
    python3 .claude/scripts/tickets/ticket_tree.py home      --ticket T0.07
    python3 .claude/scripts/tickets/ticket_tree.py status    --ticket T0.07
    python3 .claude/scripts/tickets/ticket_tree.py start     --ticket T0.07                 (worker worktree, first step)
    python3 .claude/scripts/tickets/ticket_tree.py handoff   --ticket T0.07 --task K01      (worker worktree, last step)
    python3 .claude/scripts/tickets/ticket_tree.py integrate --ticket T0.07 --task K01 [--task K02 ...] [--resolved]
    python3 .claude/scripts/tickets/ticket_tree.py diff      --ticket T0.07 [--from TREE] [--name-only]
    python3 .claude/scripts/tickets/ticket_tree.py changes   --ticket T0.07 [--write | --check]
    python3 .claude/scripts/tickets/ticket_tree.py docs      --ticket T0.07                 (prints nothing when all is well)
    python3 .claude/scripts/tickets/ticket_tree.py finish    --ticket T0.07 [--no-pull-request]

Every ticket lives in its own worktree, its *home*: ``<repository>-tickets/<ID>/`` beside the main checkout, on the
GitFlow branch ``feature/<ID>`` (TKT-15). The main checkout stays on ``develop``, so several tickets run at once
(TKT-16). Nothing is committed before ``finish``: the ticket's work stays uncommitted in its home. Instead of commits,
the script uses git *trees* (``git write-tree`` on a temporary index), which never appear in the history:

- ``prepare`` puts the main checkout on ``feature/tickets`` (from ``origin/develop``, ``develop`` without a remote)
  and records the ticket's own files. On ``develop``, it carries the uncommitted changes under ``docs/tickets/`` and
  the board cache ``.claude/github.json`` (the plans ``/issue-plan`` wrote there, L-48), and refuses any other change.
  Run again, it keeps the ticket's state and its work.
- ``home`` prints the home's path.
- ``start`` copies the home's uncommitted work into a fresh worker worktree, and records the tree it starts from in
  the worktree's git directory (``swarm-base-tree``, also read by ``.claude/hooks/check_touched.py``). A worker created
  from another commit (``develop`` moved since the ticket started) is first moved to the home's commit.
- ``handoff`` saves the worker's own changes, from that tree to its current files, as a patch in
  ``<git common dir>/swarm/<ID>/pending/``. Run it again after any later change.
- ``integrate`` applies the hand-offs to the home in the order given, stops at the first conflict (with ``.rej``
  files to resolve by hand, then ``--resolved``), removes the integrated worktrees, and records the task ids (TKT-11).
  It prints the tree of the integrated work, which ``diff --from`` compares with later. A file that another open
  ticket already owns is never applied nor taken as this ticket's own (TKT-16, L-34): it is listed under ``refused``
  with its owner and the applied patch that keeps its change, recorded in the state, and printed on stderr (L-51);
  the rest of the hand-off is integrated.
- ``changes`` writes the table of changed files and line ranges between ``<!-- changes -->`` markers of
  ``EXPLAIN.md`` (TKT-14), leaving out the ticket's own folder. Every file and every line range in it is a link.
- ``docs`` checks ``EXPLAIN.md`` and ``IMPLEMENTATION.md`` (TKT-14): the changes table is up to date, no placeholder
  is left, every file and line mentioned is a clickable relative link, and every link resolves (the file exists, the
  line ``#L<n>`` or range ``#L<a>-L<b>`` is inside it, and a ``path:42`` link text matches its ``#L42``). It prints one
  problem per line, and nothing when all is well. ``finish`` refuses to commit while it finds a problem.
- ``finish`` makes the one commit on ``feature/<ID>``. With a remote ``origin``, it rebases that commit on
  ``origin/develop`` when ``develop`` moved, pushes the branch and opens its pull request to ``develop`` (``Closes #n``,
  label ``automerge``): GitHub merges it once CI passes (TKT-15). An open pull request is updated through the REST
  API, never ``gh pr edit``, whose GraphQL query fails on the deprecated Projects (classic) (L-30, L-36). Without a
  remote, it merges the branch into ``develop`` in the main checkout with ``--no-ff``. Once the commit is pushed or
  merged, it removes the state whatever the pull request step did: a failed pull request step is reported under
  ``pull_request_error`` and in the exit code, for the person to finish by hand. The home stays until
  ``tickets.py prune`` finds the branch merged.

Each command prints JSON (or the diff or table asked for) on stdout, and a failure on stderr with exit code 1.
"""

JsonData = Union[str, int, bool, None, List["JsonData"], Dict[str, "JsonData"]]

TICKET_PATTERN = re.compile(r"^T\d\.\d{2}$")
HUNK_PATTERN = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")
DEVELOP = "develop"
REMOTE = "origin"
BRANCH_PREFIX = "feature/"
LEGACY_PREFIX = "ticket/"
TICKETS_SUFFIX = "-tickets"
SHARED_BRANCH = "feature/tickets"
FINISH_LOCK = "finish.lock"
PULL_REQUEST_ERROR = "pull_request_error"
PATHS_KEY = "paths"
REFUSED_KEY = "refused"
STOPPED_KEY = "stopped"
REASON_KEY = "reason"
NEXT_KEY = "next"
TICKET_SUBJECT = re.compile(r"^(T\d+\.\d{2})[: ]")
AUTOMERGE_LABEL = "automerge"
# L-30, L-36: ``gh pr edit`` reads the deprecated Projects (classic) and fails; the REST API does not. ``gh api`` fills in
# ``{owner}`` and ``{repo}`` from the checkout's remote.
PULLS_API = "repos/{owner}/{repo}/pulls"
ISSUES_API = "repos/{owner}/{repo}/issues"
GITHUB_STATE = ".claude/github.json"
HARNESS_FOLDER = ".claude/"
# L-48: what /ticket-plan and /issue-plan write wherever the checkout stands, and the board cache: prepare carries these
# changes of develop to the shared branch, where TKT-16 wants them uncommitted. Any other change is refused.
CARRIED_PREFIXES = ("docs/tickets/", GITHUB_STATE)
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
    """Return the worktree a ticket started in before TKT-16 shared the main checkout (``feature/<ID>``), if any."""
    for path, branch in worktrees(top):
        if branch in (ticket_branch(ticket), f"{LEGACY_PREFIX}{ticket}"):
            return path
    return None


def home_of(top: Path, ticket: str) -> Path:
    """Return the ticket's home: the main checkout, shared by every running ticket (TKT-16), or a legacy worktree."""
    return find_home(top, ticket) or main_checkout(top)


def open_states(top: Path) -> List[str]:
    """Return the tickets that have a state, prepared and not finished yet."""
    root = common_dir(top) / STATE_FOLDER
    if not root.is_dir():
        return []
    return sorted(p.name for p in root.iterdir() if TICKET_PATTERN.match(p.name) and (p / STATE_FILE).is_file())


def ticket_paths(state: Dict[str, JsonData], ticket: str) -> List[str]:
    """Return the ticket's own files: its folder and every file its tasks changed (``["."]`` before TKT-16)."""
    recorded = state.get(PATHS_KEY)
    if not isinstance(recorded, list):
        return ["."]
    return sorted({str(path) for path in recorded} | {ticket_folder(ticket)})


def owners_of_files(top: Path, ticket: str) -> Dict[str, str]:
    """Return every file or folder another open ticket owns, with that ticket (TKT-16), ``"."`` states left out."""
    owners: Dict[str, str] = {}
    for other in open_states(top):
        if other == ticket:
            continue
        state = load_state(top, other)
        if isinstance(state.get(PATHS_KEY), list):
            for path in ticket_paths(state, other):
                owners.setdefault(path, other)
    return owners


def owner_of(name: str, owners: Dict[str, str]) -> Optional[str]:
    """Return the open ticket that owns ``name``, a file it changed or a file under a folder it owns, or None."""
    for path, ticket in owners.items():
        if name == path.rstrip("/") or name.startswith(path.rstrip("/") + "/"):
            return ticket
    return None


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


def tracked_changes(top: Path) -> List[str]:
    """Return the tracked files a checkout changed, staged or not, sorted."""
    names = git(top, "diff", "--name-only", "HEAD")[1].splitlines()
    return sorted({name for name in names if name})


def is_carried(name: str) -> bool:
    """Tell whether ``prepare`` carries a change of ``develop`` to the shared branch (L-48)."""
    return any(name == prefix or name.startswith(prefix) for prefix in CARRIED_PREFIXES)


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
    """Return a file name for a task id, which may hold a path (``FIX-backend/a.py``)."""
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


def shared_start(main: Path) -> str:
    """Return where the shared branch starts: ``origin/develop`` (fetched) when there is a remote, else ``develop``."""
    if has_remote(main):
        git(main, "fetch", "--quiet", REMOTE, DEVELOP, check=False)
        remote_develop = f"{REMOTE}/{DEVELOP}"
        if git(main, "rev-parse", "--verify", "--quiet", remote_develop, check=False)[0] == 0:
            return remote_develop
    return DEVELOP


def newer_harness(home: Path, start_point: str) -> List[str]:
    """Return the harness files ``start_point`` changed since the shared branch left it (L-54).

    The harness runs from the checked-out branch, and the shared branch is never rebased while tickets are open
    (TKT-5): a harness fix merged on develop meanwhile would not reach the tickets started now.
    """
    code, out = git(home, "diff", "--name-only", f"HEAD...{start_point}", "--", HARNESS_FOLDER, check=False)
    return [line for line in out.splitlines() if line] if code == 0 else []


def prepare(top: Path, ticket: str) -> Dict[str, JsonData]:
    """Put the main checkout on the shared branch ``feature/tickets`` and record where the ticket starts (TKT-16)."""
    if is_worker(top):
        raise TicketTreeError("Run prepare in the main checkout, not in a worker worktree.")
    home = find_home(top, ticket)
    if home is None:
        home = main_checkout(top)
        branch = current_branch(home)
        others = [other for other in open_states(home) if other != ticket]
        if branch == DEVELOP:
            others_changed = [name for name in tracked_changes(home) if not is_carried(name)]
            if others_changed:
                raise TicketTreeError(
                    f"{DEVELOP} has changes to tracked files in {home} ({', '.join(others_changed)}): commit them on a "
                    f"feature branch or put them aside, then run again. The tickets work on {SHARED_BRANCH}; only "
                    f"changes under {' and '.join(CARRIED_PREFIXES)} are carried there."
                )
            start_point = shared_start(home)
            code, _ = git(home, "checkout", "--quiet", "-B", SHARED_BRANCH, start_point, check=False)
            if code != 0:
                raise TicketTreeError(
                    f"The changes of {DEVELOP} under {' and '.join(CARRIED_PREFIXES)} in {home} touch files that "
                    f"{start_point} changed, so they cannot be carried to {SHARED_BRANCH}: bring {DEVELOP} up to date "
                    f"or put them aside, then run again."
                )
        elif branch == SHARED_BRANCH:
            start_point = shared_start(home)
            caught_up = git(home, "merge-base", "--is-ancestor", "HEAD", start_point, check=False)[0] == 0
            if not others and caught_up:
                git(home, "merge", "--quiet", "--ff-only", start_point, check=False)
            newer = newer_harness(home, start_point)
            if newer and ticket not in open_states(home):
                raise TicketTreeError(
                    f"{start_point} holds a newer harness than {SHARED_BRANCH} ({', '.join(newer[:5])}"
                    f"{', ...' if len(newer) > 5 else ''}): this ticket's start rule and workflows would run the older "
                    f"one (L-54). Let the open tickets ({', '.join(others) or 'none'}) be merged first, or bring "
                    f"{start_point} into {SHARED_BRANCH} (the person runs `git merge {start_point}`), then run again."
                )
        else:
            raise TicketTreeError(
                f"The main checkout is on {branch or 'a detached HEAD'}: the tickets work on {SHARED_BRANCH}, "
                f"started from {DEVELOP}. Switch it to {DEVELOP} or {SHARED_BRANCH}, then run again."
            )
    state = load_state(home, ticket)
    state.pop(STOPPED_KEY, None)
    if not state.get("base"):
        state["base"] = head(home)
    if find_home(top, ticket) is None and PATHS_KEY not in state:
        state[PATHS_KEY] = [ticket_folder(ticket)]
    state["tree"] = snapshot(home)
    state["home"] = str(home)
    save_state(home, ticket, state)
    write_patch(home, str(state["base"]), str(state["tree"]), state_dir(home, ticket) / INTEGRATED_PATCH)
    return {
        "branch": current_branch(home),
        "home": str(home),
        "base": state["base"],
        "tree": state["tree"],
        "integrated": integrated_ids(state),
        "paths": ticket_paths(state, ticket),
    }


def stop(top: Path, ticket: str, reason: str, next_step: str) -> Dict[str, JsonData]:
    """Record that the ticket's last run stopped, why and what the person does next (L-56).

    The group report reads it and shows the ticket stopped instead of running; the next ``prepare`` clears it. A ticket
    that was never prepared has no state and records nothing.
    """
    path = state_dir(top, ticket) / STATE_FILE
    if not path.is_file():
        return {"ticket": ticket, STOPPED_KEY: None}
    state = load_state(top, ticket)
    state[STOPPED_KEY] = {REASON_KEY: reason, NEXT_KEY: next_step}
    save_state(top, ticket, state)
    return {"ticket": ticket, STOPPED_KEY: state[STOPPED_KEY]}


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
    return {
        "ticket": ticket,
        "integrated": integrated,
        "tree": state.get("tree") or "",
        "paths": ticket_paths(state, ticket),
    }


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
    owners = owners_of_files(top, ticket)
    done: List[JsonData] = []
    conflicts: List[JsonData] = []
    refused: List[JsonData] = []
    remaining = list(tasks)
    while remaining:
        task = remaining[0]
        patch = folder / PENDING / f"{slug(task)}.patch"
        meta_path = patch.with_suffix(".json")
        if not patch.is_file():
            raise TicketTreeError(f"No hand-off for {task}: the worker must run handoff --task {task}.")
        meta: Dict[str, JsonData] = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.is_file() else {}
        changed = [line.split("\t")[1:] for line in meta.get("files") or [] if isinstance(line, str)]
        names = sorted({name for names in changed for name in names})
        foreign = {name: owner for name in names if (owner := owner_of(name, owners))}
        excluded = [f"--exclude={name}" for name in foreign]
        if not resolved and patch.stat().st_size:
            apply = ["apply", "--binary", "--whitespace=nowarn", *excluded]
            code, _ = git(top, *apply, "--check", str(patch), check=False)
            if code != 0:
                git(top, *apply, "--reject", str(patch), check=False)
                conflicts.append({"task": task, "rejects": rejects(top), "patch": str(patch)})
                break
            git(top, *apply, str(patch))
        applied = folder / APPLIED
        applied.mkdir(parents=True, exist_ok=True)
        number = len(list(applied.glob("*.patch"))) + 1
        kept = applied / f"{number:03d}-{slug(task)}.patch"
        for name, owner in sorted(foreign.items()):
            refused.append({"task": task, "file": name, "owner": owner, "patch": str(kept)})
            # L-51: never silent. The change stays in the applied patch, for the person to carry once ``owner`` is done.
            print(
                f"⚠️ {task}: {name} is owned by the open ticket {owner}, so its change was not applied (TKT-16). "
                f"It is kept in {kept}.",
                file=sys.stderr,
            )
        patch.replace(kept)
        if meta_path.is_file():
            meta_path.replace(applied / f"{number:03d}-{slug(task)}.json")
        integrated = state.get("integrated")
        state["integrated"] = [*(integrated if isinstance(integrated, list) else []), task]
        if foreign:
            earlier = state.get(REFUSED_KEY)
            state[REFUSED_KEY] = [*(earlier if isinstance(earlier, list) else []), *refused[-len(foreign) :]]
        if isinstance(state.get(PATHS_KEY), list):
            state[PATHS_KEY] = sorted({*state[PATHS_KEY], *(name for name in names if name not in foreign)})
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
        REFUSED_KEY: refused,
        "remaining": remaining,
        "tree": state.get("tree") or "",
    }
    return result, 1 if conflicts else 0


def diff(top: Path, ticket: str, from_tree: Optional[str], name_only: bool) -> str:
    """Return the diff of the ticket's uncommitted work, from HEAD or from an earlier integrated tree."""
    top = require_home(top, ticket)
    base = from_tree or head(top)
    options = ["--name-status"] if name_only else ["--no-color"]
    paths = ticket_paths(load_state(top, ticket), ticket)
    return git(top, "diff", *options, base, snapshot(top), "--", *paths)[1]


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
    paths = ticket_paths(load_state(top, ticket), ticket)
    statuses: Dict[str, str] = {}
    for line in git(top, "diff", "--name-status", "-M", head(top), tree, "--", *paths, excluded)[1].splitlines():
        parts = line.split("\t")
        if len(parts) >= 2:
            code = parts[0][:1]
            name = STATUS_NAMES.get(code, code)
            statuses[parts[-1]] = f"{name} from `{parts[1]}`" if code in "RC" and len(parts) == 3 else name
    counts: Dict[str, Tuple[str, str]] = {}
    for line in git(top, "diff", "--numstat", "-M", head(top), tree, "--", *paths, excluded)[1].splitlines():
        parts = line.split("\t")
        if len(parts) == 3:
            path = parts[2]
            if " => " in path:
                path = statuses_key(path, statuses)
            counts[path] = (parts[0], parts[1])
    ranges: Dict[str, List[Tuple[int, int]]] = {}
    removed_only: Dict[str, List[int]] = {}
    current = ""
    for line in git(top, "diff", "-U0", "-M", "--no-color", head(top), tree, "--", *paths, excluded)[1].splitlines():
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


def tickets_on_branch(home: Path) -> List[Tuple[str, str]]:
    """Return (ticket, subject) of the ticket commits of the branch that ``develop`` does not hold yet, oldest first."""
    base = f"{REMOTE}/{DEVELOP}" if has_remote(home) else DEVELOP
    subjects = git(home, "log", "--reverse", "--format=%s", f"{base}..HEAD", check=False)[1].splitlines()
    found: List[Tuple[str, str]] = []
    for subject in subjects:
        match = TICKET_SUBJECT.match(subject)
        if match and match.group(1) not in [ticket for ticket, _ in found]:
            found.append((match.group(1), subject))
    return found


def pull_request(home: Path, branch: str) -> str:
    """Open the pull request of ``branch`` to ``develop``, or update the open one: one ``Closes`` per ticket on it."""
    tickets = tickets_on_branch(home)
    lines = [
        f"Closes #{number}: {subject}" if (number := issue_number(home, ticket)) else f"{subject} (no issue)"
        for ticket, subject in tickets
    ]
    body = "\n".join(
        [
            *lines,
            "",
            (
                "One commit per ticket (TKT-5), each worked by the harness and reviewed by the person before the push "
                "(TKT-18). Each ticket's `docs/tickets/<ID>/` holds its EXPLAIN.md, IMPLEMENTATION.md, REVIEW.md and "
                "PROGRESS.md."
            ),
            "",
            "Merged into `develop` by the `automerge` workflow once the checks pass (TKT-15).",
        ]
    )
    if len(tickets) == 1:
        title = tickets[0][1]
    else:
        title = f"Tickets {', '.join(ticket for ticket, _ in tickets)}"
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
    code, listed = run_tool(home, "gh", "pr", "list", "--head", branch, "--state", "open", "--json", "number,url")
    try:
        found = json.loads(listed) if code == 0 and listed else []
    except json.JSONDecodeError:
        found = []
    if isinstance(found, list) and found and isinstance(found[0], dict):
        number, url = found[0].get("number"), str(found[0].get("url") or "")
        updates = (
            ("api", "-X", "PATCH", f"{PULLS_API}/{number}", "-f", f"title={title}", "-f", f"body={body}"),
            ("api", "-X", "POST", f"{ISSUES_API}/{number}/labels", "-f", f"labels[]={AUTOMERGE_LABEL}"),
        )
        for update in updates:
            code, output = run_tool(home, "gh", *update)
            if code != 0:
                raise TicketTreeError(f"The branch is pushed but its pull request could not be updated: {output}")
        return url
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


def publish(home: Path, ticket: str, open_pull_request: bool) -> Dict[str, JsonData]:
    """Push the branch that holds the ticket's commit and open or update its pull request (TKT-15)."""
    branch = current_branch(home)
    code, output = git(home, "push", "--quiet", "--set-upstream", REMOTE, branch, check=False)
    if code != 0:
        code, output = git(home, "push", "--quiet", "--force-with-lease", "--set-upstream", REMOTE, branch, check=False)
    if code != 0:
        raise TicketTreeError(f"git push {REMOTE} {branch} failed: {output}")
    result: Dict[str, JsonData] = {"pushed": True, "branch": branch}
    if open_pull_request:
        try:
            result["pull_request"] = pull_request(home, branch)
        except TicketTreeError as error:
            print(f"note: the pull request step failed after the push ({type(error).__name__}).", file=sys.stderr)
            result[PULL_REQUEST_ERROR] = str(error)
            return result
        board = home / ".claude" / "scripts" / "github" / "board.py"
        if board.is_file():
            run_tool(home, sys.executable, str(board), "move", "--ticket", ticket, "--status", "review")
    return result


def merge_locally(home: Path, ticket: str) -> str:
    """Merge the ticket's branch into ``develop`` with ``--no-ff``, when there is no remote to open a pull request on."""
    branch = current_branch(home)
    message = f"{ticket}: merge {branch} into {DEVELOP}"
    main = main_checkout(home)
    if current_branch(main) == DEVELOP:
        if not is_clean(main):
            raise TicketTreeError(f"The ticket is committed on {branch}, but {DEVELOP} has changes: merge it by hand.")
        target = main
    else:
        target = Path(tempfile.mkdtemp(prefix="swarm-develop-"))
        target.rmdir()
        git(main, "worktree", "add", "--quiet", str(target), DEVELOP)
    try:
        code, output = git(target, "merge", "--no-ff", "--quiet", branch, "-m", message, check=False)
        if code != 0:
            git(target, "merge", "--abort", check=False)
            raise TicketTreeError(f"{DEVELOP} does not merge {branch} cleanly: {output}")
        return head(target)
    except TicketTreeError as error:
        print(f"note: the merge into {DEVELOP} stopped ({type(error).__name__}).", file=sys.stderr)
        raise
    finally:
        if target != main:
            git(main, "worktree", "remove", "--force", str(target), check=False)


def commit_paths(home: Path, paths: List[str], title: str, body: str) -> str:
    """Commit only ``paths`` of the working tree on the current branch; every other change stays uncommitted (TKT-16).

    The commit is built on a temporary index from ``HEAD`` and these paths, so the other tickets' work is never
    staged; the real index then follows the new ``HEAD`` for these paths only.
    """
    present = [
        path for path in paths if path == "." or (home / path).exists() or git(home, "ls-tree", "HEAD", "--", path)[1]
    ]
    old = head(home)
    with tempfile.TemporaryDirectory() as folder:
        index = Path(folder) / "index"
        git(home, "read-tree", "HEAD", index=index)
        git(home, "add", "-A", "--", *present, index=index)
        tree = git(home, "write-tree", index=index)[1]
    commit = git(home, "commit-tree", tree, "-p", old, "-m", title, "-m", body)[1]
    git(home, "update-ref", "-m", f"ticket_tree finish: {title}", f"refs/heads/{current_branch(home)}", commit, old)
    git(home, "reset", "--quiet", "--", *present)
    return commit


def regenerate_changes_table(top: Path, ticket: str) -> None:
    """Rewrite the changes table of ``EXPLAIN.md`` when it has its markers, so that no other commit stales it (L-42)."""
    explain = top / ticket_folder(ticket) / "EXPLAIN.md"
    if explain.is_file() and CHANGES_START in explain.read_text(encoding="utf-8"):
        changes(top, ticket, "write")


def finish(top: Path, ticket: str, open_pull_request: bool = True) -> Dict[str, JsonData]:
    """Commit the ticket's own files once on the shared branch, then publish it (TKT-15) or merge it locally."""
    home = require_home(top, ticket)
    lock_path = common_dir(home) / STATE_FOLDER / FINISH_LOCK
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open("w", encoding="utf-8") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        left = rejects(home)
        if left:
            raise TicketTreeError(f"Resolve and delete these .rej files first: {', '.join(left)}.")
        state = load_state(home, ticket)
        paths = ticket_paths(state, ticket)
        if not git(home, "diff", "--name-only", "HEAD", snapshot(home), "--", *paths)[1]:
            raise TicketTreeError("There is nothing to commit for this ticket.")
        regenerate_changes_table(home, ticket)
        problems = document_problems(home, ticket)
        if problems:
            raise TicketTreeError("Fix the ticket's documents before its commit (TKT-14):\n" + "\n".join(problems))
        title = ticket_title(home, ticket)
        tasks = integrated_ids(state)
        commit = commit_paths(home, paths, title, f"Tasks: {', '.join(tasks) or 'none recorded'}.")
        result: Dict[str, JsonData] = {"commit": commit, "home": str(home), "tasks": list(tasks)}
        if has_remote(home):
            result.update(publish(home, ticket, open_pull_request))
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
    root = argparse.ArgumentParser(description=USAGE, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = root.add_subparsers(dest="command", required=True)
    for name in ("prepare", "home", "status", "start", "handoff", "integrate", "diff", "changes", "docs", "finish", "stop"):
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
        if name == "stop":
            command.add_argument("--reason", required=True)
            command.add_argument("--next", dest="next_step", default="")
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
        elif args.command == "stop":
            output = stop(top, args.ticket, args.reason, args.next_step)
        else:
            finished = finish(top, args.ticket, not args.no_pull_request)
            output = finished
            if finished.get(PULL_REQUEST_ERROR):
                print(f"❌ Committed and pushed, but {finished[PULL_REQUEST_ERROR]}", file=sys.stderr)
                code = 1
    except TicketTreeError as error:
        print(f"❌ {error}", file=sys.stderr)
        return 1
    text = output if isinstance(output, str) else json.dumps(output)
    if text:
        print(text)
    return code


if __name__ == "__main__":
    sys.exit(main())
