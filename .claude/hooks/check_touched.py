#!/usr/bin/env python3
"""SubagentStop hook: run the checks of the touched layer before a worker hands its task back.

Usage, with the SubagentStop JSON on stdin:
    python3 .claude/hooks/check_touched.py [--dry-run]

The hook does nothing outside a linked git worktree, so the main working tree is never checked. It finds the files the
worker changed, looks up the rules of ``layer-checks.json``
that match them and runs the resulting commands from the top of the worktree. When a check fails, the hook exits 2 so
that the agent fixes it, at most ``max_blocks`` times (TKT-6); after that it exits 0 and leaves the failure to the
verifier. A missing executable is a note, not a failure. ``--dry-run`` only prints the commands.

The files the worker changed are those that differ from the tree recorded by ``ticket_tree.py start`` (the file
``swarm-base-tree`` in the worktree's git directory): the work of earlier tasks copied in by ``start`` is not the
worker's, so it is not checked again (TKT-5). Without that file, they are the files committed since the base,
modified, added or untracked.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple

TIMEOUT_S = 600
COUNTER_NAME = "swarm-check-touched-blocks"
BASE_TREE_FILE = "swarm-base-tree"
COMMIT_PATTERN = re.compile(r"^(T\d\.\d{2}) K\d{2}:")
TESTS_PATTERN = re.compile(r"(^|/)tests/")
TAIL_LINES = 20


def git(cwd: Path, *args: str) -> Tuple[int, str]:
    """Run a git command and return its exit code and its standard output."""
    try:
        result = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=False)
    except (FileNotFoundError, NotADirectoryError):
        return 127, ""
    return result.returncode, result.stdout.strip()


def worktree_info(cwd: Path) -> Optional[Tuple[Path, Path]]:
    """Return the top and the git directory of a linked worktree, or None when cwd is anywhere else."""
    code, top = git(cwd, "rev-parse", "--show-toplevel")
    if code != 0 or not top:
        return None
    _, git_dir = git(cwd, "rev-parse", "--absolute-git-dir")
    _, common = git(cwd, "rev-parse", "--git-common-dir")
    resolved_dir = Path(git_dir).resolve()
    if resolved_dir == (Path(top) / common).resolve():
        return None
    return Path(top), resolved_dir


def branch_exists(top: Path, branch: str) -> bool:
    """Tell whether a local branch exists."""
    return git(top, "rev-parse", "--verify", "--quiet", f"refs/heads/{branch}")[0] == 0


def find_base(top: Path) -> Optional[str]:
    """Return the merge-base of HEAD with the ticket branch, else with develop, else None."""
    _, subjects = git(top, "log", "--format=%s", "-n", "200")
    ticket = next((m.group(1) for m in map(COMMIT_PATTERN.match, subjects.splitlines()) if m), None)
    branch = f"ticket/{ticket}" if ticket and branch_exists(top, f"ticket/{ticket}") else "develop"
    if not branch_exists(top, branch):
        return None
    code, base = git(top, "merge-base", branch, "HEAD")
    return base if code == 0 and base else None


def snapshot(top: Path) -> Optional[str]:
    """Return the tree of every file of the worktree, tracked or not, through a temporary copy of its index."""
    code, real = git(top, "rev-parse", "--git-path", "index")
    if code != 0:
        return None
    real_index = Path(real) if Path(real).is_absolute() else top / real
    with tempfile.TemporaryDirectory() as folder:
        index = Path(folder) / "index"
        if real_index.is_file():
            shutil.copy2(real_index, index)
        env = {**os.environ, "GIT_INDEX_FILE": str(index)}
        added = subprocess.run(["git", "add", "-A"], cwd=top, env=env, capture_output=True, text=True, check=False)
        tree = subprocess.run(["git", "write-tree"], cwd=top, env=env, capture_output=True, text=True, check=False)
    if added.returncode != 0 or tree.returncode != 0:
        return None
    return tree.stdout.strip()


def changed_files(top: Path, git_dir: Optional[Path] = None) -> List[str]:
    """Return the sorted, existing files the worker changed: since its start tree, else since the base."""
    marker = git_dir / BASE_TREE_FILE if git_dir else None
    if marker is not None and marker.is_file():
        tree = snapshot(top)
        if tree:
            names = git(top, "diff", "--name-only", marker.read_text(encoding="utf-8").strip(), tree)[1].splitlines()
            return sorted(f for f in names if f and (top / f).exists())
    found = set()
    base = find_base(top)
    if base:
        found.update(git(top, "diff", "--name-only", base, "HEAD")[1].splitlines())
    entries = subprocess.run(
        ["git", "status", "--porcelain", "-z", "-uall"], cwd=top, capture_output=True, text=True, check=False
    ).stdout.split("\0")
    index = 0
    while index < len(entries):
        entry = entries[index]
        index += 1
        if len(entry) > 3:
            found.add(entry[3:])
            if entry[0] in "RC":
                index += 1
    return sorted(f for f in found if f and (top / f).exists())


def load_catalogue(top: Path) -> Dict[str, object]:
    """Load the catalogue of the worktree, else the one beside this script."""
    here = Path(__file__).resolve().with_name("layer-checks.json")
    for path in (top / ".claude" / "hooks" / "layer-checks.json", here):
        if path.is_file():
            return json.loads(path.read_text(encoding="utf-8"))
    return {"max_blocks": 2, "rules": []}


def substitute(text: str, groups: Tuple[str, ...]) -> str:
    """Replace ``{1}``, ``{2}``... with the captured groups."""
    for number, value in enumerate(groups, start=1):
        text = text.replace(f"{{{number}}}", value)
    return text


def plan_commands(top: Path, rules: List[Dict[str, object]], files: List[str]) -> List[Tuple[str, List[str]]]:
    """Return the (name, argv) pairs to run, in rule order, without duplicates."""
    only_tests = bool(files) and all(TESTS_PATTERN.search(f) for f in files)
    commands: List[Tuple[str, List[str]]] = []
    for rule in rules:
        if rule.get("skip_when_only_tests") and only_tests:
            continue
        groups: Dict[Tuple[str, ...], List[str]] = {}
        for file in files:
            found = re.search(str(rule["match"]), file)
            if found:
                groups.setdefault(found.groups(), []).append(file)
        for captured, members in groups.items():
            needs = rule.get("needs")
            if needs and not (top / substitute(str(needs), captured)).exists():
                continue
            argv: List[str] = []
            for item in list(rule["run"]):  # type: ignore[call-overload]
                if item == "{files}":
                    argv.extend(members)
                else:
                    argv.append(substitute(str(item), captured))
            pair = (substitute(str(rule["name"]), captured), argv)
            if pair not in commands:
                commands.append(pair)
    return commands


def run_command(top: Path, argv: List[str]) -> Tuple[int, str]:
    """Run one command from the top of the worktree and return its exit code and output."""
    try:
        result = subprocess.run(argv, cwd=top, capture_output=True, text=True, timeout=TIMEOUT_S, check=False)
    except FileNotFoundError:
        return 127, f"command not found: {argv[0]}"
    except subprocess.TimeoutExpired:
        return 124, f"timed out after {TIMEOUT_S} s"
    return result.returncode, (result.stdout + result.stderr).strip()


def read_counter(path: Path) -> int:
    """Return the number of times the agent was already sent back."""
    try:
        return int(path.read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        return 0


def main() -> int:
    """Run the hook and return its exit code."""
    dry_run = "--dry-run" in sys.argv[1:]
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        payload = {}
    cwd = Path(str(payload.get("cwd") or Path.cwd()))
    info = worktree_info(cwd) if cwd.is_dir() else None
    if info is None:
        return 0
    top, git_dir = info
    catalogue = load_catalogue(top)
    rules = list(catalogue["rules"])  # type: ignore[call-overload]
    commands = plan_commands(top, rules, changed_files(top, git_dir))
    if dry_run:
        for name, argv in commands:
            print(f"{name}: {' '.join(argv)}")
        return 0
    failures: List[Tuple[str, str]] = []
    for name, argv in commands:
        code, output = run_command(top, argv)
        if code == 127:
            print(f"note: {name} skipped, {argv[0]} is not installed.", file=sys.stderr)
        elif code != 0:
            failures.append((name, "\n".join(output.splitlines()[-TAIL_LINES:])))
    counter = git_dir / COUNTER_NAME
    if not failures:
        counter.unlink(missing_ok=True)
        return 0
    blocks = read_counter(counter)
    if blocks >= int(catalogue.get("max_blocks", 2)):  # type: ignore[call-overload]
        names = ", ".join(name for name, _ in failures)
        print(f"note: checks still failing ({names}), the verifier will report them.", file=sys.stderr)
        return 0
    counter.write_text(str(blocks + 1), encoding="utf-8")
    for name, tail in failures:
        print(f"❌ {name}\n{tail}", file=sys.stderr)
    print("Fix these failures within the files of your task, or report the task as blocked.", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
