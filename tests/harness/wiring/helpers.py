from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, List


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def read_text(relative: str) -> str:
    return (repo_root() / relative).read_text(encoding="utf-8")


def read_json(relative: str) -> Dict[str, object]:
    return json.loads(read_text(relative))


def agent_frontmatter(path: Path) -> Dict[str, str]:
    lines = path.read_text(encoding="utf-8").split("\n")
    fields: Dict[str, str] = {}
    if not lines or lines[0].strip() != "---":
        return fields
    for line in lines[1:]:
        if line.strip() == "---":
            break
        key, separator, value = line.partition(":")
        if separator:
            fields[key.strip()] = value.strip()
    return fields


def agent_body(path: Path) -> str:
    parts = path.read_text(encoding="utf-8").split("\n---\n", 1)
    return parts[1] if len(parts) > 1 else ""


def agent_files() -> List[Path]:
    return sorted((repo_root() / ".claude" / "agents").glob("*.md"))


def agent_path(name: str) -> Path:
    return repo_root() / ".claude" / "agents" / f"{name}.md"


def phase_titles(relative: str) -> List[str]:
    parts = read_text(relative).split("phases:", 1)
    if len(parts) < 2:
        return []
    return re.findall(r"title:\s*'([^']+)'", parts[1].split("]", 1)[0])
