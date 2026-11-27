from __future__ import annotations

# Standard library imports
import json
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

# Third-party imports
import pytest
from pydantic import JsonValue

TICKET = "T9.07"
DRIVER = Path(__file__).resolve().parent / "run_workflow.mjs"
DONE: Dict[str, JsonValue] = {
    "status": "done",
    "worktree": "",
    "files_changed": [],
    "checks": [],
    "assumptions": [],
    "decisions": [],
    "blocked_by": [],
}


def task(task_id: str, files: List[str], wave: int = 1, agent: str = "implementer") -> Dict[str, JsonValue]:
    return {"id": task_id, "title": f"Task {task_id}", "agent": agent, "depends_on": [], "files": files, "wave": wave}


def gate(tasks: List[Dict[str, JsonValue]]) -> Dict[str, JsonValue]:
    return {
        "approved": True,
        "status": "**Plan:** 🟢 Approved",
        "tasks": tasks,
        "done_tasks": [],
        "push_approved": False,
        "push_status": "",
    }


def blocked(file: str, problem: str) -> Dict[str, JsonValue]:
    return {**DONE, "status": "blocked", "blocked_by": [{"file": file, "problem": problem}]}


def failing(file: str, environment: bool = False) -> Dict[str, JsonValue]:
    failure = {"check": "pytest", "file": file, "detail": "assert 1 == 2", "environment": environment}
    return {"passed": False, "failures": [failure], "not_applicable": []}


def rule(
    reply: JsonValue,
    agent_type: str = "",
    label: str = "",
    prompt: str = "",
    times: Optional[int] = None,
) -> Dict[str, JsonValue]:
    found: Dict[str, JsonValue] = {"reply": reply, "agentType": agent_type, "label": label, "prompt": prompt}
    if times is not None:
        found["times"] = times
    return found


def run_workflow(
    tmp_path: Path, tasks: List[Dict[str, JsonValue]], rules: List[Dict[str, JsonValue]]
) -> Dict[str, JsonValue]:
    """Run ticket-run.js with stand-in agents and return its result, every agent call and every log line."""
    if shutil.which("node") is None:
        pytest.skip("node is not installed")
    scenario = tmp_path / "scenario.json"
    scenario.write_text(json.dumps({"args": TICKET, "gate": gate(tasks), "rules": rules}), encoding="utf-8")
    result = subprocess.run(["node", str(DRIVER), str(scenario)], capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr
    loaded: Dict[str, JsonValue] = json.loads(result.stdout.splitlines()[-1])
    return loaded


def labels(run: Dict[str, JsonValue]) -> List[str]:
    calls = run["calls"]
    assert isinstance(calls, list)
    return [str(call["label"]) for call in calls if isinstance(call, dict)]


def prompts(run: Dict[str, JsonValue], label: str) -> List[str]:
    calls = run["calls"]
    assert isinstance(calls, list)
    return [str(call["prompt"]) for call in calls if isinstance(call, dict) and label in str(call["label"])]
