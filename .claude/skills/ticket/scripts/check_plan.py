"""Check the task graph of a ticket's PLAN.md (TKT-3, TKT-4).

Usage, from anywhere:
    python3 .claude/skills/ticket/scripts/check_plan.py <ID> [--root <repo root>] [--min-parallel N]

It reads ``<root>/docs/tickets/<ID>/PLAN.md`` and prints one line per problem,
``docs/tickets/<ID>/PLAN.md: <message>``, then exits 1. When the plan is sound it prints nothing and exits 0. A bad
ID gives the usage on stderr and exit 2. The default root is the repository holding the script, and the default
``--min-parallel`` is 1.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set

ID_PATTERN = re.compile(r"^T\d\.\d{2}$")
TASK_ID_PATTERN = re.compile(r"^K\d{2}$")
STATUS_LINES = ("**Plan:** 🟡 Awaiting approval", "**Plan:** 🟢 Approved")
JSON_BLOCK = re.compile(r"^```json[ \t]*\n(.*?)^```[ \t]*$", re.MULTILINE | re.DOTALL)
AGENTS = (
    "test-writer",
    "implementer",
    "rust-implementer",
    "frontend-implementer",
    "mockup-writer",
    "doc-writer",
)
IMPLEMENTERS = ("implementer", "rust-implementer", "frontend-implementer")
USAGE = "usage: check_plan.py <ID> [--root <repo root>] [--min-parallel N]"
Task = Dict[str, object]


def is_int(value: object) -> bool:
    """Tell whether a value is an integer, rejecting booleans."""
    return isinstance(value, int) and not isinstance(value, bool)


def check_fields(task: Task, label: str, known: Set[str]) -> List[str]:
    """Check the fields of one task."""
    problems: List[str] = []
    for key in ("title", "brief", "done_when"):
        value = task.get(key)
        if not isinstance(value, str) or not value.strip():
            problems.append(f"task {label}: missing or empty {key}: {value!r}.")
    agent = task.get("agent")
    if agent not in AGENTS:
        problems.append(f"task {label}: unknown agent: {agent!r}.")
    deps = task.get("depends_on")
    if not isinstance(deps, list):
        problems.append(f"task {label}: depends_on must be a list: {deps!r}.")
    else:
        for dep in deps:
            if not isinstance(dep, str) or dep not in known:
                problems.append(f"task {label}: unknown dependency: {dep!r}.")
    files = task.get("files")
    if not isinstance(files, list) or not files or not all(isinstance(f, str) and f for f in files):
        problems.append(f"task {label}: files must be a non-empty list of strings: {files!r}.")
    wave = task.get("wave")
    if not is_int(wave) or wave < 1:  # type: ignore[operator]
        problems.append(f"task {label}: wave must be an integer of 1 or more: {wave!r}.")
    return problems


def find_cycle(graph: Dict[str, List[str]]) -> List[str]:
    """Return the ids of the tasks that sit on a cycle, or an empty list."""
    on_cycle: Set[str] = set()
    for start, first in graph.items():
        stack = [(start, iter(first))]
        path = [start]
        while stack:
            children = stack[-1][1]
            child = next(children, None)
            if child is None:
                stack.pop()
                path.pop()
            elif child in path:
                on_cycle.update(path[path.index(child) :])
            elif child in graph:
                stack.append((child, iter(graph[child])))
                path.append(child)
    return sorted(on_cycle)


def ancestors(task_id: str, graph: Dict[str, List[str]]) -> Set[str]:
    """Return every transitive dependency of a task."""
    seen: Set[str] = set()
    todo = list(graph.get(task_id, []))
    while todo:
        current = todo.pop()
        if current not in seen:
            seen.add(current)
            todo.extend(graph.get(current, []))
    return seen


def check_graph(tasks: List[Task], min_parallel: int) -> List[str]:
    """Check the plan as a whole."""
    problems: List[str] = []
    ids: List[str] = []
    for task in tasks:
        task_id = task.get("id")
        if not isinstance(task_id, str) or not TASK_ID_PATTERN.match(task_id):
            problems.append(f"task id must match K<nn>: {task_id!r}.")
        elif task_id in ids:
            problems.append(f"duplicate task id: {task_id!r}.")
        else:
            ids.append(task_id)
    known = set(ids)
    for task in tasks:
        task_id = task.get("id")
        label = repr(task_id) if not isinstance(task_id, str) else task_id
        problems.extend(check_fields(task, label, known))

    valid = [t for t in tasks if isinstance(t.get("id"), str) and t["id"] in known]
    graph: Dict[str, List[str]] = {}
    agents: Dict[str, object] = {}
    waves: Dict[str, int] = {}
    for task in valid:
        task_id = str(task["id"])
        deps = task.get("depends_on")
        graph[task_id] = [d for d in deps if isinstance(d, str) and d in known] if isinstance(deps, list) else []
        agents[task_id] = task.get("agent")
        wave = task.get("wave")
        if is_int(wave) and isinstance(wave, int) and wave >= 1:
            waves[task_id] = wave

    for task_id in find_cycle(graph):
        problems.append(f"task {task_id}: depends_on forms a cycle.")
    for task_id, deps in graph.items():
        for dep in deps:
            if task_id in waves and dep in waves and waves[task_id] <= waves[dep]:
                problems.append(f"task {task_id}: wave {waves[task_id]} is not after {dep} in wave {waves[dep]}.")
    owners: Dict[tuple, str] = {}
    for task in valid:
        task_id = str(task["id"])
        files = task.get("files")
        if task_id not in waves or not isinstance(files, list):
            continue
        for path in files:
            if not isinstance(path, str):
                continue
            key = (waves[task_id], path)
            if key in owners and owners[key] != task_id:
                problems.append(f"tasks {owners[key]} and {task_id} share {path!r} in wave {waves[task_id]}.")
            else:
                owners[key] = task_id
    for task_id, agent in agents.items():
        if agent == "test-writer" and task_id in waves and waves[task_id] != 1:
            problems.append(f"task {task_id}: test-writer must be in wave 1, not {waves[task_id]}.")
        if agent in IMPLEMENTERS and not any(agents.get(a) == "test-writer" for a in ancestors(task_id, graph)):
            problems.append(f"task {task_id}: {agent} has no test-writer among its dependencies.")
    if waves:
        counts: Dict[int, int] = {}
        for wave in waves.values():
            counts[wave] = counts.get(wave, 0) + 1
        widest = max(counts.values())
        if widest < min_parallel:
            problems.append(f"the widest wave holds {widest} tasks, fewer than the {min_parallel} required.")
    elif min_parallel > 1:
        problems.append(f"no wave holds the {min_parallel} tasks required.")
    return problems


def check_plan(path: Path, min_parallel: int) -> List[str]:
    """Check one PLAN.md file."""
    if not path.is_file():
        return [f"file not found: {path.name!r}."]
    text = path.read_text(encoding="utf-8")
    problems: List[str] = []
    lines = [line.strip() for line in text.splitlines()]
    if not any(line in STATUS_LINES for line in lines):
        found = next((line for line in lines if line.startswith("**Plan:**")), "none")
        problems.append(f"status line must be {STATUS_LINES[0]!r} or {STATUS_LINES[1]!r}: found {found!r}.")
    blocks = JSON_BLOCK.findall(text)
    if len(blocks) != 1:
        problems.append(f"expected exactly one json block: found {len(blocks)}.")
        return problems
    try:
        data = json.loads(blocks[0])
    except json.JSONDecodeError as error:
        problems.append(f"the json block does not parse: {error}.")
        return problems
    if not isinstance(data, list) or not all(isinstance(item, dict) for item in data):
        problems.append("the json block must be an array of objects.")
        return problems
    problems.extend(check_graph(data, min_parallel))
    return problems


def main(argv: Optional[List[str]] = None) -> int:
    """Run the check from the command line."""
    args = list(sys.argv[1:] if argv is None else argv)
    root = Path(__file__).resolve().parents[4]
    min_parallel = 1
    ticket_id: Optional[str] = None
    try:
        while args:
            arg = args.pop(0)
            if arg == "--root":
                root = Path(args.pop(0))
            elif arg == "--min-parallel":
                min_parallel = int(args.pop(0))
            elif ticket_id is None and not arg.startswith("--"):
                ticket_id = arg
            else:
                raise ValueError(arg)
    except (IndexError, ValueError):
        print(USAGE, file=sys.stderr)
        return 2
    if ticket_id is None or not ID_PATTERN.match(ticket_id):
        print(f"{USAGE}\nbad ticket id: {ticket_id!r}.", file=sys.stderr)
        return 2
    relative = f"docs/tickets/{ticket_id}/PLAN.md"
    problems = check_plan(root / relative, min_parallel)
    for problem in problems:
        print(f"{relative}: {problem}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
