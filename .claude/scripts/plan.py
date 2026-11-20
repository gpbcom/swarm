#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

ROOT = Path(__file__).resolve().parents[2]
START = "<!-- plan:graph -->"
END = "<!-- /plan:graph -->"
JSON_BLOCK = re.compile(r"^```json[ \t]*\n(.*?)\n```[ \t]*$", re.DOTALL | re.MULTILINE)
FENCE_LINE = re.compile(r"^\s*(```|~~~)")
CODE_SPAN = re.compile(r"(`+)(.+?)\1", re.DOTALL)
AGENT_ICONS = {
    "test-writer": "🧪",
    "implementer": "🐍",
    "rust-implementer": "🦀",
    "frontend-implementer": "🖥️",
    "mockup-writer": "✏️",
    "doc-writer": "📝",
}
# Mermaid classes per agent, so that the graph shows at a glance which kind of worker does what.
AGENT_STYLES = {
    "test-writer": "fill:#fff4d6,stroke:#b8860b,color:#3d2e00",
    "implementer": "fill:#dbeafe,stroke:#1d4ed8,color:#0b1f4d",
    "rust-implementer": "fill:#fde2d4,stroke:#c2410c,color:#4a1a05",
    "frontend-implementer": "fill:#e0f2f1,stroke:#0f766e,color:#053b36",
    "mockup-writer": "fill:#f3e8ff,stroke:#7e22ce,color:#2e0b4f",
    "doc-writer": "fill:#e5e7eb,stroke:#4b5563,color:#111827",
}

Task = Dict[str, Union[str, int, List[str]]]


class PlanError(Exception):
    """Raised when a PLAN.md cannot be rendered without changing its data."""


def read_graph(text: str) -> Tuple[re.Match[str], List[Task]]:
    blocks = list(JSON_BLOCK.finditer(text))
    if len(blocks) != 1:
        raise PlanError(f"expected exactly one ```json block, found {len(blocks)}")
    try:
        graph = json.loads(blocks[0].group(1))
    except json.JSONDecodeError as error:
        raise PlanError(f"the json block does not parse: {error}") from error
    if not isinstance(graph, list) or not all(isinstance(task, dict) for task in graph):
        raise PlanError("the json block is not an array of task objects")
    for task in graph:
        for key in ("id", "title", "agent", "depends_on", "files", "brief", "done_when", "wave"):
            if key not in task:
                raise PlanError(f"task {task.get('id', '?')} has no {key!r}")
    return blocks[0], graph


def anchor(task_id: str) -> str:
    return task_id.lower()


def link(task_id: str) -> str:
    return f"[{task_id}](#{anchor(task_id)})"


def links(task_ids: List[str]) -> str:
    return ", ".join(link(task_id) for task_id in task_ids) if task_ids else "none"


def cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", "<br>")


def agent_label(agent: str) -> str:
    return f"{AGENT_ICONS.get(agent, '🤖')} {agent}"


def prose(text: str) -> str:
    """Return the text as Markdown that shows every character, or a fenced block if it would break the page."""
    if any(FENCE_LINE.match(line) for line in text.splitlines()):
        fence = "~" * max(4, 1 + max((len(m) for m in re.findall(r"~+", text)), default=0))
        return f"{fence}text\n{text}\n{fence}"
    # Inline runs of three backticks (such as "one ```json block") would open a code span that swallows the text,
    # and would read as a second json block to a careless parser: show them as HTML entities instead.
    text = re.sub(r"`{3,}", lambda match: "&#96;" * len(match.group(0)), text)
    # Outside code spans, an HTML-like ``<ID>`` would be hidden by the Markdown viewer: escape it.
    parts: List[str] = []
    last = 0
    for match in CODE_SPAN.finditer(text):
        parts.append(text[last : match.start()].replace("<", "&lt;"))
        parts.append(match.group(0))
        last = match.end()
    parts.append(text[last:].replace("<", "&lt;"))
    return "".join(parts)


def mermaid_label(task: Task) -> str:
    title = str(task["title"]).replace("`", "").replace('"', "#quot;").replace("<", "#lt;").replace(">", "#gt;")
    return f'"{task["id"]} · {agent_label(str(task["agent"]))}<br/>{title}"'


def render_view(graph: List[Task]) -> str:
    waves = sorted({int(task["wave"]) for task in graph})
    unblocks: Dict[str, List[str]] = {str(task["id"]): [] for task in graph}
    for task in graph:
        for dependency in task["depends_on"]:
            unblocks.setdefault(str(dependency), []).append(str(task["id"]))
    lines: List[str] = [START, ""]
    lines += [
        "> [!NOTE]",
        "> Generated from the json block at the end of this page by `python3 .claude/scripts/plan.py render`.",
        "> To change a task, edit the json block, then render again: never edit this view by hand.",
        "",
        "## Waves",
        "",
        "| Wave | Tasks | Agents running at once |",
        "| --- | --- | --- |",
    ]
    for wave in waves:
        in_wave = [task for task in graph if int(task["wave"]) == wave]
        lines.append(
            f"| {wave} | {', '.join(link(str(task['id'])) for task in in_wave)} | {min(len(in_wave), 8)} of {len(in_wave)} |"
        )
    lines += ["", "| Wave | Task | Agent | Depends on | Unblocks |", "| --- | --- | --- | --- | --- |"]
    for task in graph:
        task_id = str(task["id"])
        lines.append(
            f"| {task['wave']} | {link(task_id)} {cell(str(task['title']))} | {agent_label(str(task['agent']))} "
            f"| {links([str(d) for d in task['depends_on']])} | {links(unblocks[task_id])} |"
        )
    lines += ["", "## Dependency graph", "", "```mermaid", "flowchart LR"]
    for wave in waves:
        lines.append(f'  subgraph W{wave}["Wave {wave}"]')
        lines.append("    direction TB")
        for task in graph:
            if int(task["wave"]) == wave:
                lines.append(f"    {task['id']}[{mermaid_label(task)}]:::{str(task['agent']).replace('-', '_')}")
        lines.append("  end")
    for task in graph:
        for dependency in task["depends_on"]:
            lines.append(f"  {dependency} --> {task['id']}")
    for agent in sorted({str(task["agent"]) for task in graph}):
        style = AGENT_STYLES.get(agent, "fill:#ffffff,stroke:#333333,color:#000000")
        lines.append(f"  classDef {agent.replace('-', '_')} {style}")
    lines += ["```", "", "## Tasks", ""]
    for task in graph:
        task_id = str(task["id"])
        lines += [
            f'### <a id="{anchor(task_id)}"></a>{task_id}: {task["title"]}',
            "",
            "| Agent | Wave | Depends on | Unblocks |",
            "| --- | --- | --- | --- |",
            (
                f"| {agent_label(str(task['agent']))} | {task['wave']} | {links([str(d) for d in task['depends_on']])} "
                f"| {links(unblocks[task_id])} |"
            ),
            "",
            "**Files** (only this task may change them in its wave):",
            "",
        ]
        lines += [f"- `{path}`" for path in task["files"]] or ["- none"]
        lines += [
            "",
            f"**Done when:** {prose(str(task['done_when']))}",
            "",
            "**Brief:**",
            "",
            prose(str(task["brief"])),
            "",
        ]
    lines.append(END)
    return "\n".join(lines)


def render(text: str) -> str:
    block, graph = read_graph(text)
    pretty = json.dumps(graph, indent=2, ensure_ascii=False)
    folded = (
        "<details>\n<summary>🤖 Task graph as read by <code>/ticket-run</code> (json)</summary>\n\n"
        f"```json\n{pretty}\n```\n\n</details>"
    )
    before, after = text[: block.start()], text[block.end() :]
    before = re.sub(r"<details>\n<summary>[^\n]*</summary>\n\n$", "", before)
    after = re.sub(r"^\n\n</details>", "", after)
    text = before + folded + after
    view = render_view(graph)
    if START in text and END in text:
        text = text[: text.index(START)] + view + text[text.index(END) + len(END) :]
    else:
        text = re.sub(r"^## Waves\n.*?(?=^## )", "", text, count=1, flags=re.DOTALL | re.MULTILINE)
        heading = re.search(r"^## Task graph", text, re.MULTILINE)
        position = heading.start() if heading else len(text)
        text = text[:position] + view + "\n\n" + text[position:]
    _, again = read_graph(text)
    if again != graph:
        raise PlanError("rendering changed the task graph; nothing was written")
    return text


def show(graph: List[Task], command: str, task_id: Optional[str]) -> int:
    """Print the outline of the graph, or the brief and done-when of one task."""
    if command == "outline":
        outline = [{key: value for key, value in task.items() if key not in ("brief", "done_when")} for task in graph]
        print(json.dumps(outline, ensure_ascii=False))
        return 0
    task = next((task for task in graph if task["id"] == task_id), None)
    if task is None:
        print(f"Unknown task: {task_id!r}. Known: {', '.join(str(t['id']) for t in graph)}.")
        return 1
    print(f"# {task['id']}: {task['title']}\n\n## Brief\n\n{task['brief']}\n\n## Done when\n\n{task['done_when']}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Render the task graph of a PLAN.md for people.")
    parser.add_argument("command", choices=("render", "check", "outline", "task"))
    parser.add_argument("--ticket", required=True)
    parser.add_argument("--id", help="The task id, for the task command.")
    arguments = parser.parse_args()
    if not re.fullmatch(r"T\d\.\d{2}", arguments.ticket):
        parser.error(f"Invalid ticket: {arguments.ticket!r}. Must look like T1.07.")
    if arguments.command == "task" and not arguments.id:
        parser.error("The task command needs --id, such as --id K07.")
    path = ROOT / "docs" / "tickets" / arguments.ticket / "PLAN.md"
    try:
        text = path.read_text(encoding="utf-8")
        if arguments.command in ("outline", "task"):
            return show(read_graph(text)[1], arguments.command, arguments.id)
        rendered = render(text)
    except (OSError, PlanError) as error:
        print(f"{path.relative_to(ROOT)}: {error}")
        return 1
    if arguments.command == "check":
        if rendered != text:
            print(
                f"{path.relative_to(ROOT)}: the readable view is out of date. Run plan.py render --ticket {arguments.ticket}."
            )
            return 1
        return 0
    if rendered != text:
        path.write_text(rendered, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
