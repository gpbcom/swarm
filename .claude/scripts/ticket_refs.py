#!/usr/bin/env python3
"""Keep the specification references of a ticket in its TICKET.md, PLAN.md and PROGRESS.md (TKT-2).

Usage, from the repository root:
    python3 .claude/scripts/ticket_refs.py sync --ticket T0.02
    python3 .claude/scripts/ticket_refs.py check --ticket T0.02

A specification reference is a relative link to a technical page (``docs/specs/technical/<page>.md``, its overview
excepted) or to a feature, a use case or a business rule (``docs/specs/functional/{features,use-cases,
business-rules}/``). ``TICKET.md`` is their only source and must hold at least one, each resolving to an existing
page and anchor. ``sync`` copies them, in order and without duplicates, into a generated ``## 📚 Specifications``
section of ``PLAN.md`` and ``PROGRESS.md``, between the ``<!-- ticket:specs -->`` markers, just under the status line.
``check`` prints one line per problem (no reference, a broken link, a missing or stale section) and exits 1, or
prints nothing.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import List, Optional, Tuple

ROOT = Path(__file__).resolve().parents[2]
SPECS = ROOT / "docs" / "specs"
START = "<!-- ticket:specs -->"
END = "<!-- /ticket:specs -->"
LINK = re.compile(r"(?<!!)\[([^\]]+)\]\(([^)\s]+)\)")
KINDS = ("functional/features", "functional/use-cases", "functional/business-rules", "technical")
STATUS_LINE = re.compile(r"^\*\*(Plan|Status):\*\*.*$", re.MULTILINE)


def spec_kind(target: Path) -> Optional[str]:
    try:
        relative = target.relative_to(SPECS).as_posix()
    except ValueError:
        return None
    if relative == "technical/README.md" or not relative.endswith(".md"):
        return None
    return next((kind for kind in KINDS if relative.startswith(f"{kind}/")), None)


def references(ticket_md: Path) -> Tuple[List[Tuple[str, str]], List[str]]:
    """Return the specification links of TICKET.md as (text, href), and the problems of those links."""
    found: List[Tuple[str, str]] = []
    problems: List[str] = []
    seen = set()
    for text, href in LINK.findall(ticket_md.read_text(encoding="utf-8")):
        if re.match(r"^[a-z]+:", href):
            continue
        path_part, _, anchor = href.partition("#")
        target = (ticket_md.parent / path_part).resolve()
        if spec_kind(target) is None:
            continue
        if not target.is_file():
            problems.append(f"the link {href!r} points to a page that does not exist")
            continue
        if anchor and f'<a id="{anchor}"></a>' not in target.read_text(encoding="utf-8"):
            problems.append(f"the link {href!r} points to an anchor that does not exist")
            continue
        if href not in seen:
            seen.add(href)
            found.append((text, href))
    if not found and not problems:
        problems.append(
            "no link to a technical page, a feature, a use case or a business rule. "
            "Link the specification the ticket builds on, or write it first."
        )
    return found, problems


def section(found: List[Tuple[str, str]]) -> str:
    lines = [
        START,
        "## 📚 Specifications",
        "",
        (
            "The technical pages, features, use cases and business rules of [TICKET.md](TICKET.md), copied by "
            "`python3 .claude/scripts/ticket_refs.py sync`."
        ),
        "",
    ]
    lines += [f"- [{text}]({href})" for text, href in found]
    lines.append(END)
    return "\n".join(lines)


def with_section(text: str, block: str) -> str:
    if START in text and END in text:
        return text[: text.index(START)] + block + text[text.index(END) + len(END) :]
    status = STATUS_LINE.search(text)
    if status is None:
        heading = re.search(r"^# .*$", text, re.MULTILINE)
        position = heading.end() if heading else 0
    else:
        position = status.end()
    return text[:position] + "\n\n" + block + "\n\n" + text[position:].lstrip("\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Keep the specification references of a ticket's documents.")
    parser.add_argument("command", choices=("sync", "check"))
    parser.add_argument("--ticket", required=True)
    arguments = parser.parse_args()
    if not re.fullmatch(r"T\d\.\d{2}", arguments.ticket):
        parser.error(f"Invalid ticket: {arguments.ticket!r}. Must look like T1.07.")
    folder = ROOT / "docs" / "tickets" / arguments.ticket
    ticket_md = folder / "TICKET.md"
    if not ticket_md.is_file():
        print(f"{ticket_md.relative_to(ROOT)}: the file does not exist.")
        return 1
    found, problems = references(ticket_md)
    lines = [f"{ticket_md.relative_to(ROOT)}: {problem}" for problem in problems]
    if found:
        block = section(found)
        for name in ("PLAN.md", "PROGRESS.md"):
            path = folder / name
            if not path.is_file():
                continue
            current = path.read_text(encoding="utf-8")
            wanted = with_section(current, block)
            if wanted == current:
                continue
            if arguments.command == "sync":
                path.write_text(wanted, encoding="utf-8")
            elif START in current:
                lines.append(f"{path.relative_to(ROOT)}: the 📚 Specifications section is out of date. Run sync.")
            else:
                lines.append(f"{path.relative_to(ROOT)}: the 📚 Specifications section is missing. Run sync.")
    for line in lines:
        print(line)
    return 1 if lines else 0


if __name__ == "__main__":
    sys.exit(main())
