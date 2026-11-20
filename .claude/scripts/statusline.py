#!/usr/bin/env python3
"""Claude Code status line of Swarm: the GitFlow branch, the open tickets and the board, from local files only.

Configured in ``.claude/settings.json`` (``statusLine``). Reads the session's JSON on stdin and prints one line:

    🌿 feature/T0.09 · 🎫 T0.09 🔄 · open 🔄T0.09 👀T0.10 · 🗂️ ✅6 📝1 🔄1 👀1 🏁8/262 · 🧠 Opus

The board counts come from ``.git/swarm/board.json``, written by ``board.py`` (``sync``, ``move``, ``bootstrap``),
so the line never waits for GitHub.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List

ICONS = {"backlog": "📥", "ready": "✅", "planned": "📝", "running": "🔄", "review": "👀", "done": "🏁"}
SHOWN = ("ready", "planned", "running", "review")
BRANCH_ICONS = {"feature": "🌿", "release": "🚀", "hotfix": "🚑", "bugfix": "🐛", "develop": "🧪", "master": "🏷️"}
TICKET = re.compile(r"^T\d+\.\d{2}$")


def git(cwd: str, *args: str) -> str:
    result = subprocess.run(["git", "-C", cwd, *args], capture_output=True, text=True, check=False, timeout=2)
    return result.stdout.strip()


def line(payload: Dict[str, object]) -> str:
    workspace = payload.get("workspace")
    cwd = str(workspace.get("current_dir")) if isinstance(workspace, dict) else str(payload.get("cwd") or ".")
    branch = git(cwd, "branch", "--show-current") or "detached"
    parts: List[str] = [f"{BRANCH_ICONS.get(branch.split('/')[0], '🔀')} {branch}"]
    common = git(cwd, "rev-parse", "--path-format=absolute", "--git-common-dir")
    cache_path = Path(common) / "swarm" / "board.json" if common else None
    status: Dict[str, str] = {}
    if cache_path and cache_path.is_file():
        status = json.loads(cache_path.read_text(encoding="utf-8")).get("status", {})
    current = branch.split("/", 1)[1] if branch.startswith("feature/") else ""
    if TICKET.match(current):
        parts.append(f"🎫 {current} {ICONS.get(status.get(current, 'running'), '🔄')}")
    legacy = re.findall(r"branch refs/heads/feature/(T\d+\.\d{2})", git(cwd, "worktree", "list", "--porcelain"))
    states = Path(common) / "swarm" if common else None
    shared = sorted(p.name for p in states.iterdir() if TICKET.match(p.name)) if states and states.is_dir() else []
    open_tickets = sorted(set(shared) | set(legacy))
    if open_tickets:
        parts.append("open " + " ".join(f"{ICONS.get(status.get(t, 'running'), '🔄')}{t}" for t in open_tickets))
    tickets = {k: v for k, v in status.items() if TICKET.match(k)}
    if tickets:
        counts = " ".join(f"{ICONS[s]}{sum(1 for v in tickets.values() if v == s)}" for s in SHOWN)
        done = sum(1 for v in tickets.values() if v == "done")
        parts.append(f"🗂️ {counts} 🏁{done}/{len(tickets)}")
    model = payload.get("model")
    if isinstance(model, dict) and model.get("display_name"):
        parts.append(f"🧠 {model['display_name']}")
    return " · ".join(parts)


def main() -> int:
    try:
        payload = json.loads(sys.stdin.read() or "{}")
        print(line(payload if isinstance(payload, dict) else {}))
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        print(f"🔀 swarm · status line: {type(error).__name__}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
