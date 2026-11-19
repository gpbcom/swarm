from __future__ import annotations

# Standard library imports
import copy
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional

from pydantic import JsonValue

TICKET_ID = "T9.99"
APPROVED = "**Plan:** 🟢 Approved"
AWAITING = "**Plan:** 🟡 Awaiting approval"
REJECTED = "**Plan:** 🔴 Rejected"


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def script_path() -> Path:
    return repo_root() / ".claude" / "skills" / "ticket" / "scripts" / "check_plan.py"


def a_task(
    task_id: str,
    agent: str,
    wave: int,
    depends_on: Optional[List[str]] = None,
    files: Optional[List[str]] = None,
) -> Dict[str, JsonValue]:
    return {
        "id": task_id,
        "title": f"Task {task_id}",
        "agent": agent,
        "depends_on": depends_on if depends_on is not None else [],
        "files": files if files is not None else [f"src/{task_id.lower()}.py"],
        "brief": f"Do {task_id}.",
        "done_when": f"{task_id} is done.",
        "wave": wave,
    }


def sample_tasks() -> List[Dict[str, JsonValue]]:
    return [
        a_task("K01", "test-writer", 1),
        a_task("K02", "test-writer", 1),
        a_task("K03", "test-writer", 1),
        a_task("K04", "implementer", 2, ["K01"]),
        a_task("K05", "implementer", 2, ["K02"]),
        a_task("K06", "implementer", 2, ["K03"]),
        a_task("K07", "doc-writer", 1),
    ]


def without_key(key: str) -> List[Dict[str, JsonValue]]:
    tasks = sample_tasks()
    del tasks[0][key]
    return tasks


def with_change(index: int, key: str, value: JsonValue) -> List[Dict[str, JsonValue]]:
    tasks = sample_tasks()
    tasks[index][key] = value
    return tasks


def with_cycle() -> List[Dict[str, JsonValue]]:
    tasks = sample_tasks()
    tasks[0]["depends_on"] = ["K04"]
    return tasks


def with_cycle_and_rising_waves() -> List[Dict[str, JsonValue]]:
    tasks = sample_tasks()
    tasks[0]["depends_on"] = ["K04"]
    tasks[0]["wave"] = 3
    tasks[3]["wave"] = 4
    return tasks


def with_shared_file() -> List[Dict[str, JsonValue]]:
    tasks = sample_tasks()
    tasks[1]["files"] = copy.deepcopy(tasks[0]["files"])
    return tasks


def with_implementer_without_test_writer() -> List[Dict[str, JsonValue]]:
    tasks = sample_tasks()
    tasks[3]["depends_on"] = ["K07"]
    return tasks


def with_duplicate_id() -> List[Dict[str, JsonValue]]:
    tasks = sample_tasks()
    tasks.append(a_task("K01", "doc-writer", 1))
    return tasks


def json_block(tasks: List[Dict[str, JsonValue]]) -> str:
    return "```json\n" + json.dumps(tasks, indent=2) + "\n```\n"


def plan_text(status_line: str, body: str) -> str:
    return f"# Plan\n\n{status_line}\n\n{body}"


def write_plan_text(root: Path, text: str) -> Path:
    path = root / "docs" / "tickets" / TICKET_ID / "PLAN.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def write_plan(root: Path, status_line: str, tasks: List[Dict[str, JsonValue]]) -> Path:
    return write_plan_text(root, plan_text(status_line, json_block(tasks)))


def run_script(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script_path()), *args],
        capture_output=True,
        text=True,
        check=False,
    )
