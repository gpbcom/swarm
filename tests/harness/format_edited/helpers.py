from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional

HOOK_RELATIVE = ".claude/hooks/format_edited.py"
CATALOGUE_RELATIVE = ".claude/hooks/formatters.json"

TEMP_FORMATTERS: List[Dict[str, object]] = [
    {
        "name": "upper",
        "match": r"\.txt$",
        "run": [
            "python3",
            "-c",
            "import pathlib, sys; p = pathlib.Path(sys.argv[1]); p.write_text(p.read_text().upper())",
            "{file}",
        ],
    },
    {"name": "broken", "match": r"\.bad$", "run": ["python3", "-c", "import sys; sys.exit(3)", "{file}"]},
    {"name": "absent", "match": r"\.none$", "run": ["swarm-no-such-formatter-executable", "{file}"]},
]


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def git(folder: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-c", "user.name=Test", "-c", "user.email=test@example.com", *args],
        cwd=folder,
        check=True,
        capture_output=True,
    )


def make_repo(folder: Path) -> Path:
    folder.mkdir(parents=True, exist_ok=True)
    git(folder, "init")
    catalogue = folder / CATALOGUE_RELATIVE
    catalogue.parent.mkdir(parents=True, exist_ok=True)
    catalogue.write_text(json.dumps({"formatters": TEMP_FORMATTERS}), encoding="utf-8")
    git(folder, "add", ".")
    git(folder, "commit", "-m", "init")
    return folder


def run_hook(payload: Dict[str, object], cwd: Optional[Path] = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(repo_root() / HOOK_RELATIVE)],
        check=False,
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        cwd=cwd,
        timeout=60,
    )


def payload_for(path: Path, tool_name: str = "Write", cwd: Optional[Path] = None) -> Dict[str, object]:
    return {
        "tool_name": tool_name,
        "tool_input": {"file_path": str(path)},
        "cwd": str(cwd if cwd else path.parent),
    }
