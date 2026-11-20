#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

USAGE = """Report the progress of the running Claude Code workflow (ticket harness), exhaustively, with colour icons.

Usage, from the repository root:
    python3 .claude/scripts/progress.py watch [--every 120] [--run <run id>]
    python3 .claude/scripts/progress.py once [--run <run id>]

``watch`` prints one report every ``--every`` seconds (default 120, rule TKT-9) and exits when the workflow ends (an end
event, or every agent returned and the journal quiet for 90 seconds), or
after 20 minutes without any change (stalled). Arm it with the Monitor tool: each report is one notification.
``once`` prints a single report. Without ``--run``, the most recently changed workflow of this project is used.

    python3 .claude/scripts/progress.py timings --ticket <ID> [--write]

``timings`` measures a ticket from the transcripts of every workflow run that worked on it (ticket-plan, ticket-run,
re-runs): the overall time, the time agents worked, the time waiting between runs, and per run, per phase and per step
the start, end and elapsed time (rule TKT-10). ``--write`` puts the result into ``docs/tickets/<ID>/PROGRESS.md``
between the ``<!-- timings -->`` markers (appended at the end if missing); without it, the Markdown is printed.

Legend: 🏁 ended · ⏳ running · ❌ failed · ⚠️ stalled | phases ✅ done 🔄 running ⬜ waiting |
models 🟣 opus 🔵 sonnet 🟢 haiku 🟠 fable ⚪ other | 🪙 tokens (input + output, cache reads excluded).
"""

PROJECTS = Path.home() / ".claude" / "projects"
RUNNING_TYPES = {"launched", "started", "result"}
STALL_S = 20 * 60
QUIET_END_S = 90
MODEL_ICONS = (("opus", "🟣 opus"), ("sonnet", "🔵 sonnet"), ("haiku", "🟢 haiku"), ("fable", "🟠 fable"))


def worktrees() -> list[tuple[Path, str]]:
    """Return every checkout of the repository with its branch, the main checkout first (``git worktree list``)."""
    here = Path(__file__).resolve().parents[2]
    try:
        out = subprocess.run(
            ["git", "-C", str(here), "worktree", "list", "--porcelain"], capture_output=True, text=True, check=True
        ).stdout
    except (OSError, subprocess.CalledProcessError):
        return [(here, "")]
    found: list[tuple[Path, str]] = []
    for block in out.strip().split("\n\n"):
        fields = dict(line.split(" ", 1) for line in block.splitlines() if " " in line)
        if "worktree" in fields:
            found.append((Path(fields["worktree"]), fields.get("branch", "").removeprefix("refs/heads/")))
    return found or [(here, "")]


def main_checkout() -> Path:
    """Return the main checkout, whose transcripts hold every run even when this script runs in a ticket's worktree."""
    return worktrees()[0][0]


def ticket_folder(ticket: str) -> Path:
    """Return docs/tickets/<ID>/ in the ticket's own worktree when it has one (TKT-16), else in the main checkout."""
    for path, branch in worktrees():
        if branch in (f"feature/{ticket}", f"ticket/{ticket}"):
            return path / "docs" / "tickets" / ticket
    return main_checkout() / "docs" / "tickets" / ticket


def project_dir() -> Path:
    return PROJECTS / re.sub(r"[^A-Za-z0-9]", "-", str(main_checkout()))


def find_run(run_id: str | None) -> Path | None:
    journals = list(project_dir().glob("*/subagents/workflows/*/journal.jsonl"))
    if run_id:
        journals = [j for j in journals if j.parent.name == run_id]
    return max(journals, key=lambda j: j.stat().st_mtime).parent if journals else None


def workflow_meta(run: Path) -> tuple[str, list[str]]:
    scripts = list(run.parents[2].glob(f"workflows/scripts/*-{run.name}.js"))
    if not scripts:
        return "workflow", []
    name = scripts[0].name[: -len(f"-{run.name}.js")]
    meta = scripts[0].read_text(encoding="utf-8").split("phases:", 1)
    phases = re.findall(r"title:\s*'([^']+)'", meta[1].split("]", 1)[0]) if len(meta) > 1 else []
    return name, phases


def read_jsonl(path: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def agent_stats(run: Path, agent_id: str) -> tuple[str, int, float | None]:
    meta_file = run / f"agent-{agent_id}.meta.json"
    model = json.loads(meta_file.read_text(encoding="utf-8")).get("model", "") if meta_file.exists() else ""
    transcript = run / f"agent-{agent_id}.jsonl"
    used, first, last = 0, None, None
    if transcript.exists():
        for row in read_jsonl(transcript):
            stamp = row.get("timestamp")
            if isinstance(stamp, str):
                try:
                    moment = datetime.fromisoformat(stamp).timestamp()
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


def short(seconds: float | None) -> str:
    if seconds is None:
        return "?"
    minutes, secs = divmod(int(seconds), 60)
    return f"{minutes}m{secs:02d}s"


def summarise(result: object) -> str:
    if not isinstance(result, dict):
        return (str(result)[:80] + "…") if result and len(str(result)) > 80 else str(result or "")
    parts: list[str] = []
    for key, value in result.items():
        if isinstance(value, list):
            parts.append(f"{key}: {len(value)}")
        elif isinstance(value, (int, float, bool)) or (isinstance(value, str) and len(value) <= 40):
            parts.append(f"{key}: {value}")
        if len(parts) == 5:
            break
    return ", ".join(parts)


def report(run: Path, started_at: float) -> tuple[str, bool]:
    name, phases = workflow_meta(run)
    events = read_jsonl(run / "journal.jsonl")
    agents: dict[str, dict[str, object]] = {}
    order: list[str] = []
    ended = None
    for event in events:
        kind = str(event.get("type", ""))
        key = str(event.get("key", ""))
        if kind == "started":
            agents[key] = {
                "label": event.get("label", "agent"),
                "phase": event.get("phase", ""),
                "id": event.get("agentId", ""),
                "done": False,
                "result": None,
            }
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
    by_model: dict[str, int] = {}
    rows: list[str] = []
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
    head = (
        "🏁" if ended and not any(w in ended for w in ("fail", "error", "abort", "kill")) else ("❌" if ended else "⏳")
    )
    lines = [
        f"{head} {name} {' '.join(tickets)} · 🕒 {time.strftime('%H:%M')} · ⏱️ {int((time.time() - started_at) // 60)} min · 🪙 {total_tokens // 1000}k tokens"
        + (f" · ended: {ended}" if ended else ""),
        "📍 Phases: " + " ▸ ".join(bar),
        f"👥 Agents: ✅ {done_count} done · 🔄 {len(agents) - done_count} running · run {run.name}",
        *rows,
        "💰 Tokens by model: "
        + (" · ".join(f"{icon} {used // 1000}k" for icon, used in by_model.items()) or "none yet"),
    ]
    return "\n".join(lines), bool(ended)


TOKEN_KINDS = (
    ("input_tokens", "in"),
    ("output_tokens", "out"),
    ("cache_creation_input_tokens", "cache_write"),
    ("cache_read_input_tokens", "cache_read"),
)


def agent_window(run: Path, agent_id: str) -> tuple[float | None, float | None, dict[str, int], str]:
    meta_file = run / f"agent-{agent_id}.meta.json"
    model = json.loads(meta_file.read_text(encoding="utf-8")).get("model", "") if meta_file.exists() else ""
    first: float | None = None
    last: float | None = None
    used = {short_name: 0 for _, short_name in TOKEN_KINDS}
    transcript = run / f"agent-{agent_id}.jsonl"
    for row in read_jsonl(transcript) if transcript.exists() else []:
        stamp = row.get("timestamp")
        if isinstance(stamp, str):
            try:
                moment = datetime.fromisoformat(stamp).timestamp()
            except ValueError:
                continue
            first = moment if first is None else min(first, moment)
            last = moment if last is None else max(last, moment)
        message = row.get("message")
        usage = message.get("usage", {}) if isinstance(message, dict) else {}
        if isinstance(usage, dict):
            for key, short_name in TOKEN_KINDS:
                used[short_name] += int(usage.get(key, 0) or 0)
    return first, last, used, model


def clock(moment: float | None) -> str:
    return datetime.fromtimestamp(moment).strftime("%Y-%m-%d %H:%M:%S") if moment else "?"


def span(seconds: float | None) -> str:
    if seconds is None:
        return "?"
    hours, rest = divmod(int(seconds), 3600)
    minutes, secs = divmod(rest, 60)
    return f"{hours}h{minutes:02d}m{secs:02d}s" if hours else f"{minutes}m{secs:02d}s"


def ticket_runs(ticket: str) -> list[Path]:
    runs = []
    for journal in project_dir().glob("*/subagents/workflows/*/journal.jsonl"):
        if any(ticket in str(e.get("label", "")) for e in read_jsonl(journal) if e.get("type") == "started"):
            runs.append(journal.parent)
    return runs


def timings(ticket: str) -> str:
    runs = []
    for run in ticket_runs(ticket):
        name, phases = workflow_meta(run)
        steps = []
        results: dict[str, object] = {}
        for event in read_jsonl(run / "journal.jsonl"):
            if event.get("type") == "result":
                results[str(event.get("key"))] = event.get("result")
        for event in read_jsonl(run / "journal.jsonl"):
            if event.get("type") != "started":
                continue
            first, last, used, model = agent_window(run, str(event.get("agentId", "")))
            result = results.get(str(event.get("key")))
            status = result.get("status") if isinstance(result, dict) else None
            icon = "🔄" if result is None else ("❌" if status in ("failed", "blocked") else "✅")
            steps.append(
                {
                    "label": str(event.get("label", "agent")),
                    "phase": str(event.get("phase", "")),
                    "first": first,
                    "last": last,
                    "tokens": used,
                    "model": model_icon(model),
                    "icon": icon,
                }
            )
        starts = [s["first"] for s in steps if s["first"]]
        ends = [s["last"] for s in steps if s["last"]]
        if starts:
            runs.append(
                {
                    "run": run.name,
                    "name": name,
                    "phases": phases,
                    "steps": steps,
                    "start": min(starts),
                    "end": max(ends),
                }
            )
    if not runs:
        return f"No workflow run found for {ticket}."
    runs.sort(key=lambda r: r["start"])
    start, end = runs[0]["start"], max(r["end"] for r in runs)
    active = sum(r["end"] - r["start"] for r in runs)

    def add(total: dict[str, int], used: dict[str, int]) -> None:
        for name, amount in used.items():
            total[name] = total.get(name, 0) + amount

    def k(value: int) -> str:
        return f"{value / 1_000_000:.2f}M" if value >= 1_000_000 else f"{value // 1000}k"

    def cells(used: dict[str, int]) -> str:
        return " | ".join(k(used.get(name, 0)) for _, name in TOKEN_KINDS) + f" | **{k(sum(used.values()))}**"

    ticket_tokens: dict[str, int] = {}
    by_model: dict[str, dict[str, int]] = {}
    for r in runs:
        for s in r["steps"]:
            add(ticket_tokens, s["tokens"])
            add(by_model.setdefault(s["model"], {}), s["tokens"])
    lines = [
        "## ⏱️ Timings",
        "",
        f"Measured from the agents' transcripts by `python3 .claude/scripts/progress.py timings --ticket {ticket}` (TKT-10).",
        "",
        "| Measure | Value |",
        "| --- | --- |",
        f"| 🕒 Ticket started | {clock(start)} |",
        f"| 🕒 Last activity | {clock(end)} |",
        f"| ⏱️ **Overall ticket time** (first start to last activity) | **{span(end - start)}** |",
        f"| 🤖 Time with agents working (sum of runs) | {span(active)} |",
        f"| ⏸️ Time between runs (approvals, fixes) | {span((end - start) - active)} |",
        f"| 🔁 Workflow runs | {len(runs)} |",
        f"| 🪙 **Tokens consumed** (input, output, cache write, cache read) | **{k(sum(ticket_tokens.values()))}** |",
        "",
        "#### 🪙 Tokens by model",
        "",
        "| Model | Input | Output | Cache write | Cache read | Total |",
        "| --- | --- | --- | --- | --- | --- |",
        *[f"| {model} | {cells(used)} |" for model, used in by_model.items()],
        f"| **All models** | {cells(ticket_tokens)} |",
    ]
    for number, run in enumerate(runs, 1):
        lines += [
            "",
            f"### {number}. {run['name']} · {clock(run['start'])} to {clock(run['end'])[11:]} · ⏱️ {span(run['end'] - run['start'])}",
            "",
            "| Phase | Start | End | Elapsed | Steps |",
            "| --- | --- | --- | --- | --- |",
        ]
        for phase in run["phases"] or sorted({s["phase"] for s in run["steps"]}):
            members = [s for s in run["steps"] if s["phase"] == phase and s["first"]]
            if members:
                p_start, p_end = min(s["first"] for s in members), max(s["last"] for s in members)
                lines.append(
                    f"| {phase} | {clock(p_start)[11:]} | {clock(p_end)[11:]} | {span(p_end - p_start)} | {len(members)} |"
                )
            else:
                lines.append(f"| {phase} | | | not run | 0 |")
        run_tokens: dict[str, int] = {}
        for s in run["steps"]:
            add(run_tokens, s["tokens"])
        lines += [
            "",
            f"Tokens of this run: {cells(run_tokens).replace(' | ', ' · ')} (input · output · cache write · cache read · total)",
            "",
            "| Step | Model | Start | End | Elapsed | Input | Output | Cache write | Cache read | Total |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
        for step in sorted(run["steps"], key=lambda s: s["first"] or 0):
            elapsed = (step["last"] - step["first"]) if step["first"] and step["last"] else None
            lines.append(
                f"| {step['icon']} {step['label']} | {step['model']} | {clock(step['first'])[11:]} | "
                f"{clock(step['last'])[11:]} | {span(elapsed)} | {cells(step['tokens'])} |"
            )
    return "\n".join(lines)


def write_timings(ticket: str, text: str) -> Path:
    path = ticket_folder(ticket) / "PROGRESS.md"
    current = path.read_text(encoding="utf-8") if path.exists() else f"# {ticket}: Progress\n"
    block = f"<!-- timings -->\n{text}\n<!-- /timings -->"
    if "<!-- timings -->" in current:
        current = re.sub(r"<!-- timings -->.*?<!-- /timings -->", lambda _: block, current, flags=re.DOTALL)
    else:
        current = f"{current.rstrip()}\n\n{block}\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(current.rstrip("\n") + "\n", encoding="utf-8")
    return path


def main() -> int:
    args = sys.argv[1:]
    if args and args[0] == "timings":
        ticket = args[args.index("--ticket") + 1] if "--ticket" in args else ""
        if not re.fullmatch(r"T\d\.\d\d", ticket):
            print("usage: progress.py timings --ticket T0.01 [--write]", file=sys.stderr)
            return 2
        text = timings(ticket)
        print(f"wrote {write_timings(ticket, text)}" if "--write" in args else text)
        return 0
    if not args or args[0] not in ("watch", "once"):
        print(USAGE, file=sys.stderr)
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
            print(
                f"⚠️ No progress for {STALL_S // 60} min: the workflow may be stalled or waiting for an approval.",
                flush=True,
            )
            return 1
        time.sleep(every)


if __name__ == "__main__":
    sys.exit(main())
