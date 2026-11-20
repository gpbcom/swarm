#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional

TOOLS = ("Edit", "Write", "MultiEdit")
TIMEOUT_S = 120
TAIL_LINES = 20


def git_top(folder: Path) -> Optional[Path]:
    """Return the git top level of a folder, or None outside a work tree."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"], cwd=folder, capture_output=True, text=True, check=False
        )
    except (FileNotFoundError, NotADirectoryError):
        return None
    out = result.stdout.strip()
    return Path(out).resolve() if result.returncode == 0 and out else None


def load_formatters(top: Path) -> List[Dict[str, object]]:
    """Load the catalogue of the work tree, else the one beside this script."""
    candidate = top / ".claude" / "hooks" / "formatters.json"
    path = candidate if candidate.is_file() else Path(__file__).resolve().parent / "formatters.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    formatters = data.get("formatters") if isinstance(data, dict) else None
    return formatters if isinstance(formatters, list) else []


def command_for(formatter: Dict[str, object], relative: str) -> List[str]:
    """Return the formatter's command with ``{file}`` replaced by the relative path."""
    parts = formatter.get("run")
    if not isinstance(parts, list):
        return []
    return [str(part).replace("{file}", relative) for part in parts]


def run_formatter(formatter: Dict[str, object], top: Path, relative: str) -> int:
    """Run one formatter on one file and return the exit code of the hook."""
    name = str(formatter.get("name", "formatter"))
    command = command_for(formatter, relative)
    if not command:
        return 0
    try:
        result = subprocess.run(command, cwd=top, capture_output=True, text=True, timeout=TIMEOUT_S, check=False)
    except FileNotFoundError:
        print(f"{name} skipped: {command[0]} is not installed.", file=sys.stderr)
        return 0
    except subprocess.TimeoutExpired:
        print(f"{name} failed on {relative}\ntimed out after {TIMEOUT_S} s", file=sys.stderr)
        return 2
    if result.returncode == 0:
        return 0
    if result.returncode == 127:
        print(f"{name} skipped: {command[0]} is not installed.", file=sys.stderr)
        return 0
    tail = (result.stdout + result.stderr).strip().splitlines()[-TAIL_LINES:]
    print(f"{name} failed on {relative}\n" + "\n".join(tail), file=sys.stderr)
    return 2


def main() -> int:
    """Format the edited file and return the exit code of the hook."""
    try:
        payload = json.load(sys.stdin)
    except ValueError:
        return 0
    if not isinstance(payload, dict) or payload.get("tool_name") not in TOOLS:
        return 0
    tool_input = payload.get("tool_input")
    raw = tool_input.get("file_path") if isinstance(tool_input, dict) else None
    if not raw or not isinstance(raw, str):
        return 0
    path = Path(raw)
    if not path.is_absolute():
        path = Path(str(payload.get("cwd") or ".")) / path
    path = path.resolve()
    if not path.is_file():
        return 0
    top = git_top(path.parent)
    if top is None:
        return 0
    try:
        relative = path.relative_to(top).as_posix()
    except ValueError:
        return 0
    for formatter in load_formatters(top):
        if re.search(str(formatter.get("match", "")), relative):
            return run_formatter(formatter, top, relative)
    return 0


if __name__ == "__main__":
    sys.exit(main())
