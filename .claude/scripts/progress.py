#!/usr/bin/env python3
"""Report the progress of the running Claude Code workflow (ticket harness), exhaustively, with colour icons.

Usage, from the repository root:
    python3 .claude/scripts/progress.py watch [--every 120] [--run <run id>]
    python3 .claude/scripts/progress.py once [--run <run id>]

``watch`` prints one report every ``--every`` seconds (default 120, rule TKT-9) and exits when the workflow ends (an end
event, or every agent returned and the journal quiet for 90 seconds), or
after 20 minutes without any change (stalled). Arm it with the Monitor tool: each report is one notification.
``once`` prints a single report. Without ``--run``, the most recently changed workflow of this project is used.

Legend: 🏁 ended · ⏳ running · ❌ failed · ⚠️ stalled | phases ✅ done 🔄 running ⬜ waiting |
models 🟣 opus 🔵 sonnet 🟢 haiku 🟠 fable ⚪ other | 🪙 tokens (input + output, cache reads excluded).
"""

from __future__ import annotations

import json
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

PROJECTS = Path.home() / ".claude" / "projects"
RUNNING_TYPES = {"launched", "started", "result"}
STALL_S = 20 * 60
QUIET_END_S = 90
MODEL_ICONS = (("opus", "🟣 opus"), ("sonnet", "🔵 sonnet"), ("haiku", "🟢 haiku"), ("fable", "🟠 fable"))


def project_dir() -> Path:
    return PROJECTS / re.sub(r"[^A-Za-z0-9]", "-", str(Path(__file__).resolve().parents[2]))


def find_run(run_id: Optional[str]) -> Optional[Path]:
    journals = list(project_dir().glob("*/subagents/workflows/*/journal.jsonl"))
    if run_id:
        journals = [j for j in journals if j.parent.name == run_id]
    return max(journals, key=lambda j: j.stat().st_mtime).parent if journals else None


def workflow_meta(run: Path) -> Tuple[str, List[str]]:
    scripts = list(run.parents[2].glob(f"workflows/scripts/*-{run.name}.js"))
    if not scripts:
        return "workflow", []
    name = scripts[0].name[: -len(f"-{run.name}.js")]
    meta = scripts[0].read_text(encoding="utf-8").split("phases:", 1)
    phases = re.findall(r"title:\s*'([^']+)'", meta[1].split("]", 1)[0]) if len(meta) > 1 else []
    return name, phases


def read_jsonl(path: Path) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def agent_stats(run: Path, agent_id: str) -> Tuple[str, int, Optional[float]]:
    meta_file = run / f"agent-{agent_id}.meta.json"
    model = json.loads(meta_file.read_text(encoding="utf-8")).get("model", "") if meta_file.exists() else ""
    transcript = run / f"agent-{agent_id}.jsonl"
    used, first, last = 0, None, None
    if transcript.exists():
        for row in read_jsonl(transcript):
            stamp = row.get("timestamp")
            if isinstance(stamp, str):
                try:
                    moment = datetime.fromisoformat(stamp.replace("Z", "+00:00")).timestamp()
                    first = moment if first is None else min(first, moment)
                    last = moment if last is None else max(last, moment)
                except ValueError:
                    pass
            message = row.get("message")
            usage = message.get("usage", {}) if isinstance(message, dict) else {}
            if isinstance(usage, dict):
                used += int(usage.get("output_tokens", 0) or 0) + int(usage.get("input_tokens", 0) or 0)
    duration = (last - first) if first is not None and last is not None else None
    return model, used, duration


def model_icon(model: str) -> str:
    return next((icon for key, icon in MODEL_ICONS if key in model), f"⚪ {model or 'model?'}")


def short(seconds: Optional[float]) -> str:
    if seconds is None:
        return "?"
    minutes, secs = divmod(int(seconds), 60)
    return f"{minutes}m{secs:02d}s"


def summarise(result: object) -> str:
    if not isinstance(result, dict):
        return (str(result)[:80] + "…") if result and len(str(result)) > 80 else str(result or "")
    parts: List[str] = []
    for key, value in result.items():
        if isinstance(value, list):
            parts.append(f"{key}: {len(value)}")
        elif isinstance(value, (int, float, bool)) or (isinstance(value, str) and len(value) <= 40):
            parts.append(f"{key}: {value}")
        if len(parts) == 5:
            break
    return ", ".join(parts)


def report(run: Path, started_at: float) -> Tuple[str, bool]:
    name, phases = workflow_meta(run)
    events = read_jsonl(run / "journal.jsonl")
    agents: Dict[str, Dict[str, object]] = {}
    order: List[str] = []
    ended = None
    for event in events:
        kind = str(event.get("type", ""))
        key = str(event.get("key", ""))
        if kind == "started":
            agents[key] = {"label": event.get("label", "agent"), "phase": event.get("phase", ""),
                           "id": event.get("agentId", ""), "done": False, "result": None}
            order.append(key)
        elif kind == "result" and key in agents:
            agents[key]["done"] = True
            agents[key]["result"] = event.get("result")
        elif kind not in RUNNING_TYPES:
            ended = kind
    quiet_s = time.time() - (run / "journal.jsonl").stat().st_mtime
    if not ended and agents and all(a["done"] for a in agents.values()) and quiet_s > QUIET_END_S:
        ended = "completed"
    tickets = sorted(set(re.findall(r"T\d\.\d\d", " ".join(str(a["label"]) for a in agents.values()))))
    total_tokens = 0
    by_model: Dict[str, int] = {}
    rows: List[str] = []
    for key in order:
        agent = agents[key]
        model, used, duration = agent_stats(run, str(agent["id"]))
        total_tokens += used
        icon = model_icon(model)
        by_model[icon] = by_model.get(icon, 0) + used
        state = "✅" if agent["done"] else ("❌" if ended else "🔄")
        line = f"  {state} {agent['label']} · {icon} · ⏱️ {short(duration)} · 🪙 {used // 1000}k"
        if agent["done"]:
            line += f" · 📝 {summarise(agent['result'])}"
        rows.append(line)
    running_phases = {str(a["phase"]) for a in agents.values() if not a["done"]}
    seen_phases = {str(a["phase"]) for a in agents.values()}
    bar = []
    for phase in phases or sorted(seen_phases):
        if phase in running_phases and not ended:
            bar.append(f"🔄 {phase}")
        elif phase in seen_phases:
            bar.append(f"✅ {phase}")
        else:
            bar.append(f"⬜ {phase}")
    done_count = sum(1 for a in agents.values() if a["done"])
    head = "🏁" if ended and not any(w in ended for w in ("fail", "error", "abort", "kill")) else ("❌" if ended else "⏳")
    lines = [
        f"{head} {name} {' '.join(tickets)} · 🕒 {time.strftime('%H:%M')} · ⏱️ {int((time.time() - started_at) // 60)} min · 🪙 {total_tokens // 1000}k tokens"
        + (f" · ended: {ended}" if ended else ""),
        "📍 Phases: " + " ▸ ".join(bar),
        f"👥 Agents: ✅ {done_count} done · 🔄 {len(agents) - done_count} running · run {run.name}",
        *rows,
        "💰 Tokens by model: " + (" · ".join(f"{icon} {used // 1000}k" for icon, used in by_model.items()) or "none yet"),
    ]
    return "\n".join(lines), bool(ended)


def main() -> int:
    args = sys.argv[1:]
    if not args or args[0] not in ("watch", "once"):
        print(__doc__, file=sys.stderr)
        return 2
    every = int(args[args.index("--every") + 1]) if "--every" in args else 120
    run_id = args[args.index("--run") + 1] if "--run" in args else None
    run = find_run(run_id)
    if run is None:
        print("⚠️ No workflow found for this project.")
        return 1
    started_at = min(f.stat().st_mtime for f in run.iterdir())
    if args[0] == "once":
        print(report(run, started_at)[0], flush=True)
        return 0
    last_change, last_size = time.time(), -1
    while True:
        text, ended = report(run, started_at)
        print(text, flush=True)
        if ended:
            return 0
        size = (run / "journal.jsonl").stat().st_size
        if size != last_size:
            last_size, last_change = size, time.time()
        elif time.time() - last_change > STALL_S:
            print(f"⚠️ No progress for {STALL_S // 60} min: the workflow may be stalled or waiting for an approval.", flush=True)
            return 1
        time.sleep(every)


if __name__ == "__main__":
    sys.exit(main())
