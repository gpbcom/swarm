from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))

from roadmap_gantt import areas

ID_PATTERN = re.compile(r"^T\d\.\d{2}$")
STATUSES = ("🟡 Planned", "🔵 In progress", "✅ Done")
HEADINGS = (
    "Roadmap",
    "What it delivers",
    "Features, use cases and business rules",
    "Technical pages it builds on",
    "Screens touched",
    "Budgets touched",
    "Acceptance criteria",
    "Out of scope",
)
OPTIONAL_HEADING = "Assumptions"
ROADMAP_KEYS = ("Ticket", "Phase", "Sprint", "Epic")
LINK = re.compile(r"\[([^\]]*)\]\(([^)\s]+)\)")
SPEC_ID = re.compile(r"\b(FS|UC|BR)-(\d{3})\b")
COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
FOLDERS = {"FS": "features", "UC": "use-cases", "BR": "business-rules"}
BUDGETS_PAGE = "docs/specs/technical/07-scalability.md"
USAGE = "usage: check_ticket.py <ID> [--root <repo root>]"
EM_DASH = "—"
Section = Dict[str, str]
GRAPH = Path("docs/specs/roadmap/gantt/ticket-graph.json")
SCREEN_PNG = re.compile(r"(?:^|/)specs/screens/(UC-\d{3})/([a-z0-9-]+)\.png$")
SCREEN_ROW = re.compile(r"(?:^|/)specs/functional/use-cases/(UC-\d{3})-[^#]*\.md#screen-([a-z0-9-]+)$")
NO_SCREEN = re.compile(r"^- ➖ No screen: \S.{9,}$", re.MULTILINE)
FRONT_END_PREFIX = "frontends/"


def split_target(target: str) -> Tuple[str, str]:
    """Split a link target into its path and its anchor."""
    path, _, anchor = target.partition("#")
    return path, anchor


def is_external(target: str) -> bool:
    """Tell whether a link leaves the repository."""
    return target.startswith(("http://", "https://", "mailto:"))


def logical_target(ticket_id: str, path: str) -> str:
    """Return a link path as a normalised path relative to the root, with forward slashes."""
    return os.path.normpath(f"docs/tickets/{ticket_id}/{path}").replace(os.sep, "/")


def screens_of(body: str) -> List[Tuple[str, str]]:
    """Return the screens a "Screens touched" section links to, as (use case, node), once each (TKT-21)."""
    found: List[Tuple[str, str]] = []
    for _, target in LINK.findall(COMMENT.sub("", body)):
        match = SCREEN_PNG.search(target) or SCREEN_ROW.search(target)
        if match and not target.endswith(".dark.png") and (match.group(1), match.group(2)) not in found:
            found.append((match.group(1), match.group(2)))
    return found


def has_no_screen_reason(body: str) -> bool:
    """Tell whether a "Screens touched" section says why the ticket shows no screen (``- ➖ No screen: <why>``)."""
    return bool(NO_SCREEN.search(COMMENT.sub("", body)))


def touches_front_end(ticket_id: str, root: Path) -> bool:
    """Tell whether the ticket graph says the ticket changes a front end (``frontends/``)."""
    path = root / GRAPH
    if not path.is_file():
        return False
    info = json.loads(path.read_text(encoding="utf-8")).get("tickets", {}).get(ticket_id, {})
    return any(area.startswith(FRONT_END_PREFIX) for area in areas(str(info.get("area", ""))))


def screens_section(text: str) -> str:
    """Return the body of the "Screens touched" section of a TICKET.md."""
    return sections_of(text)[1].get("Screens touched", "")


def check_front_end(bodies: Section, ticket_id: str, root: Path) -> List[str]:
    """A ticket that changes a front end lists the screens it shows, or says why it shows none (TKT-21)."""
    body = bodies.get("Screens touched", "")
    if not touches_front_end(ticket_id, root) or screens_of(body) or has_no_screen_reason(body):
        return []
    return [
        (
            "the ticket changes a front end: 'Screens touched' must link every screen it shows (its screenshots are "
            "captured by the ticket), or say '- ➖ No screen: <why>' (TKT-21)."
        )
    ]


def sections_of(text: str) -> Tuple[List[str], Section]:
    """Return the ``## `` headings in order, and the body of each, comments removed."""
    headings: List[str] = []
    bodies: Section = {}
    current: Optional[str] = None
    for line in COMMENT.sub("", text).splitlines():
        if line.startswith("## "):
            current = line[3:].strip()
            headings.append(current)
            bodies[current] = ""
        elif current is not None:
            bodies[current] += line + "\n"
    return headings, bodies


def check_head(text: str, ticket_id: str) -> List[str]:
    """Check the title and the status line."""
    problems: List[str] = []
    lines = COMMENT.sub("", text).strip().splitlines()
    first = lines[0] if lines else ""
    match = re.match(rf"^# {re.escape(ticket_id)}: (.+)$", first)
    if not match or not match.group(1).strip():
        problems.append(f"the first line must be '# {ticket_id}: <title>': {first!r}.")
    status = re.search(r"^\*\*Status:\*\* (.*)$", text, re.MULTILINE)
    if not status:
        problems.append("missing the '**Status:**' line.")
    elif status.group(1).strip() not in STATUSES:
        problems.append(f"unknown status: {status.group(1).strip()!r}. Use one of {', '.join(STATUSES)}.")
    return problems


def check_headings(headings: List[str]) -> List[str]:
    """Check that the headings are the template's, in order."""
    problems: List[str] = []
    allowed = (*HEADINGS, OPTIONAL_HEADING)
    for heading in HEADINGS:
        if heading not in headings:
            problems.append(f"missing heading: {heading!r}.")
    for heading in headings:
        if heading not in allowed:
            problems.append(f"unknown heading: {heading!r}.")
    known = [h for h in headings if h in allowed]
    wanted = [h for h in allowed if h in known]
    for found, expected in zip(known, wanted):
        if found != expected:
            problems.append(f"heading out of order: {found!r}, expected {expected!r} here.")
    return problems


def check_roadmap(body: str, ticket_id: str, root: Path) -> List[str]:
    """Check the Roadmap section and the roadmap page of the ticket."""
    problems: List[str] = []
    lines: Dict[str, str] = {}
    for key in ROADMAP_KEYS:
        found = re.search(rf"^- \*\*{key}:\*\*(.*)$", body, re.MULTILINE)
        if found:
            lines[key] = found.group(1)
        else:
            problems.append(f"the Roadmap section has no '- **{key}:**' line: {key!r}.")
    link = LINK.search(lines.get("Ticket", ""))
    if "Ticket" in lines and not link:
        problems.append(f"the Ticket line has no link: {lines['Ticket'].strip()!r}.")
    if link:
        path, _ = split_target(link.group(2))
        logical = logical_target(ticket_id, path)
        page = root / logical
        if not logical.startswith("docs/specs/roadmap/"):
            problems.append(f"the Ticket link must target a page under docs/specs/roadmap/: {link.group(2)!r}.")
        elif page.is_file() and ticket_id not in page.read_text(encoding="utf-8"):
            problems.append(f"the roadmap page {link.group(2)!r} does not contain {ticket_id}.")
    return problems


def check_ids(text: str, root: Path) -> List[str]:
    """Check that every FS, UC and BR ID is the ID of an existing page."""
    problems: List[str] = []
    for kind, number in sorted(set(SPEC_ID.findall(COMMENT.sub("", text)))):
        folder = root / "docs" / "specs" / "functional" / FOLDERS[kind]
        if not list(folder.glob(f"{kind}-{number}-*.md")):
            problems.append(f"unknown {kind}-{number}: no page {kind}-{number}-*.md under {folder.name}/.")
    return problems


def anchors_of(page: Path) -> List[str]:
    """Return the ``id`` anchors of a Markdown page."""
    return re.findall(r'id="([^"]+)"', page.read_text(encoding="utf-8"))


def check_links(text: str, ticket_id: str, root: Path) -> List[str]:
    """Check that every relative link resolves and that links to specification pages show their ID."""
    problems: List[str] = []
    for label, target in LINK.findall(COMMENT.sub("", text)):
        if is_external(target):
            continue
        path, anchor = split_target(target)
        logical = logical_target(ticket_id, path) if path else f"docs/tickets/{ticket_id}/TICKET.md"
        page = root / logical
        if not page.is_file():
            problems.append(f"broken link, the file does not exist: {target!r}.")
        elif anchor and page.suffix == ".md" and anchor not in anchors_of(page):
            problems.append(f"broken link, the anchor does not exist: {target!r}, anchor {anchor!r}.")
        spec = SPEC_ID.match(Path(path).name) if path else None
        if spec and f"functional/{FOLDERS[spec.group(1)]}/" in logical and spec.group(0) not in label:
            problems.append(f"the link text {label!r} must show the ID {spec.group(0)} of {target!r}.")
    return problems


def check_touched(bodies: Section, ticket_id: str) -> List[str]:
    """Check the Screens touched and Budgets touched sections."""
    problems: List[str] = []
    for heading in ("Screens touched", "Budgets touched"):
        body = bodies.get(heading)
        if body is None:
            continue
        if not body.strip():
            problems.append(f"the section {heading!r} is empty.")
        for _, target in LINK.findall(body):
            if is_external(target):
                continue
            path, anchor = split_target(target)
            logical = logical_target(ticket_id, path)
            if heading == "Budgets touched":
                if logical != BUDGETS_PAGE or anchor != "budgets":
                    problems.append(f"a budget link must target 07-scalability.md#budgets: {target!r}.")
            elif logical.startswith("docs/specs/screens/"):
                continue
            elif not (logical.startswith("docs/specs/functional/use-cases/") and anchor.startswith("screen-")):
                problems.append(f"a screen link must target docs/specs/screens/ or a use case screen: {target!r}.")
    return problems


def check_criteria(bodies: Section) -> List[str]:
    """Check that the acceptance criteria are numbered and written Given, when, then."""
    body = bodies.get("Acceptance criteria")
    if body is None:
        return []
    items: List[Tuple[str, str]] = []
    for line in body.splitlines():
        numbered = re.match(r"^(\d+)\.\s(.*)$", line)
        if numbered:
            items.append((numbered.group(1), numbered.group(2)))
        elif items and line.strip():
            items[-1] = (items[-1][0], f"{items[-1][1]} {line.strip()}")
    if not items:
        return ["'Acceptance criteria' has no numbered criterion."]
    problems: List[str] = []
    for number, content in items:
        for word in ("Given", "when", "then"):
            if f"**{word}**" not in content:
                problems.append(f"acceptance criterion {number} lacks '**{word}**'.")
    return problems


def check_text(text: str) -> List[str]:
    """Check for placeholders and em dashes."""
    problems: List[str] = []
    for placeholder in sorted(set(re.findall(r"\{\{[^}]*\}?\}?", text))):
        problems.append(f"placeholder left in the ticket: {placeholder!r}.")
    if EM_DASH in text:
        problems.append("the ticket has an em dash. Use a comma, a colon or a full stop.")
    return problems


def check_ticket(ticket_id: str, root: Path) -> List[str]:
    """Return every problem of one ticket, prefixed with the file path."""
    relative = f"docs/tickets/{ticket_id}/TICKET.md"
    ticket = root / relative
    if not ticket.is_file():
        return [f"{relative}: the file does not exist: {ticket_id}."]
    text = ticket.read_text(encoding="utf-8")
    headings, bodies = sections_of(text)
    problems = check_head(text, ticket_id) + check_headings(headings)
    if "Roadmap" in bodies:
        problems += check_roadmap(bodies["Roadmap"], ticket_id, root)
    problems += check_ids(text, root) + check_links(text, ticket_id, root)
    problems += check_touched(bodies, ticket_id) + check_front_end(bodies, ticket_id, root)
    problems += check_criteria(bodies) + check_text(text)
    return [f"{relative}: {problem}" for problem in problems]


def parse_args(argv: List[str]) -> Optional[Tuple[str, Path]]:
    """Return the ID and the root, or None when the arguments are wrong."""
    root = Path(__file__).resolve().parents[4]
    args = list(argv)
    if "--root" in args:
        index = args.index("--root")
        if index + 1 >= len(args):
            return None
        root = Path(args[index + 1])
        del args[index : index + 2]
    if len(args) != 1 or not ID_PATTERN.match(args[0]):
        return None
    return args[0], root


def main(argv: Optional[List[str]] = None) -> int:
    """Run the check and return the exit code."""
    parsed = parse_args(sys.argv[1:] if argv is None else argv)
    if parsed is None:
        print(USAGE, file=sys.stderr)
        return 2
    problems = check_ticket(*parsed)
    for problem in problems:
        print(problem)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
