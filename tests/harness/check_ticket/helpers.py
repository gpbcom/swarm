from __future__ import annotations

import os
from pathlib import Path
from typing import List, Tuple

TICKET_ID = "T0.03"
ROADMAP_LINK = "../../specs/roadmap/01-p0-foundations.md"
BUDGETS_LINK = "../../specs/technical/07-scalability.md#budgets"
EM_DASH = "—"
HEADINGS: Tuple[str, ...] = (
    "Roadmap",
    "What it delivers",
    "Features, use cases and business rules",
    "Technical pages it builds on",
    "Screens touched",
    "Budgets touched",
    "Acceptance criteria",
    "Out of scope",
)


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def script_path() -> Path:
    return repo_root() / ".claude" / "skills" / "ticket" / "scripts" / "check_ticket.py"


def template_path() -> Path:
    return repo_root() / ".claude" / "skills" / "ticket" / "templates" / "TICKET.md"


def ticket_file(root: Path, ticket_id: str = TICKET_ID) -> Path:
    return root / "docs" / "tickets" / ticket_id / "TICKET.md"


def first_page(folder: str, prefix: str) -> Path:
    return min((repo_root() / "docs" / "specs" / "functional" / folder).glob(f"{prefix}-*.md"))


def first_light_screen() -> Path:
    screens = repo_root() / "docs" / "specs" / "screens"
    return min(p for p in screens.glob("UC-*/*.png") if not p.name.endswith(".dark.png"))


def page_id(page: Path) -> str:
    return page.name[:6]


def valid_ticket_text(ticket_id: str = TICKET_ID) -> str:
    feature = first_page("features", "FS")
    use_case = first_page("use-cases", "UC")
    rule = first_page("business-rules", "BR")
    screen = first_light_screen().relative_to(repo_root() / "docs" / "specs")
    lines: List[str] = [
        f"# {ticket_id}: Convention tests and linters",
        "",
        "**Status:** 🟡 Planned",
        "",
        "## Roadmap",
        "",
        f"- **Ticket:** [{ticket_id}]({ROADMAP_LINK}#s01) in [🛣️ P0: Foundations]({ROADMAP_LINK})",
        f"- **Phase:** [🛣️ P0: Foundations]({ROADMAP_LINK})",
        f"- **Sprint:** [S01]({ROADMAP_LINK}#s01), 4 to 15 January 2027",
        f"- **Epic:** [E0.1]({ROADMAP_LINK}#epics): Mono-repo",
        "",
        "## What it delivers",
        "",
        "Tests that enforce the rules.",
        "",
        "## Features, use cases and business rules",
        "",
        f"- [📘 {page_id(feature)}: Feature](../../specs/functional/features/{feature.name})",
        f"- [🎬 {page_id(use_case)}: Use case](../../specs/functional/use-cases/{use_case.name})",
        f"- [📏 {page_id(rule)}: Rule](../../specs/functional/business-rules/{rule.name})",
        "",
        "## Technical pages it builds on",
        "",
        "- [🧰 Deployment: CI/CD](../../specs/technical/09-deployment.md#ci)",
        "",
        "## Screens touched",
        "",
        f"- [Screen](../../specs/{screen.as_posix()})",
        "",
        "## Budgets touched",
        "",
        f"- [⏱️ Budgets]({BUDGETS_LINK})",
        "",
        "## Acceptance criteria",
        "",
        "1. **Given** a broken sample, **when** the tests run, **then** each rule fails once.",
        "",
        "## Out of scope",
        "",
        "- Nothing else.",
        "",
    ]
    return "\n".join(lines)


def build_root(tmp_path: Path, ticket_id: str = TICKET_ID) -> Path:
    root = tmp_path / "root"
    (root / "docs").mkdir(parents=True)
    os.symlink(repo_root() / "docs" / "specs", root / "docs" / "specs")
    target = ticket_file(root, ticket_id)
    target.parent.mkdir(parents=True)
    target.write_text(valid_ticket_text(ticket_id), encoding="utf-8")
    return root


def rewrite(root: Path, old: str, new: str, ticket_id: str = TICKET_ID) -> None:
    target = ticket_file(root, ticket_id)
    text = target.read_text(encoding="utf-8")
    assert old in text, old
    target.write_text(text.replace(old, new), encoding="utf-8")


def swap_headings(root: Path, first: str, second: str) -> None:
    rewrite(root, f"## {first}\n", "## @@swap@@\n")
    rewrite(root, f"## {second}\n", f"## {first}\n")
    rewrite(root, "## @@swap@@\n", f"## {second}\n")


def apply_fault(root: Path, fault: str) -> str:
    """Break the valid ticket in one way and return the value the message must quote."""
    feature = page_id(first_page("features", "FS"))
    use_case = page_id(first_page("use-cases", "UC"))
    rule_page = first_page("business-rules", "BR")
    rule = page_id(rule_page)
    screen = first_light_screen()
    screen_link = f"../../specs/screens/{screen.parent.name}/{screen.name}"
    match fault:
        case "unknown_feature":
            rewrite(root, f"[📘 {feature}:", "[📘 FS-999:")
            rewrite(root, f"features/{feature}", "features/FS-999")
            return "FS-999"
        case "unknown_use_case":
            rewrite(root, f"[🎬 {use_case}:", "[🎬 UC-999:")
            rewrite(root, f"use-cases/{use_case}", "use-cases/UC-999")
            return "UC-999"
        case "unknown_rule":
            rewrite(root, f"[📏 {rule}:", "[📏 BR-999:")
            rewrite(root, f"business-rules/{rule}", "business-rules/BR-999")
            return "BR-999"
        case "link_without_id":
            rewrite(root, f"[📘 {feature}: Feature]", "[📘 Feature]")
            return feature
        case "missing_file":
            rewrite(root, rule_page.name, "BR-001-nothing-here.md")
            return "BR-001-nothing-here.md"
        case "missing_anchor":
            rewrite(root, "07-scalability.md#budgets", "07-scalability.md#no-such-anchor")
            return "no-such-anchor"
        case "bad_status":
            rewrite(root, "🟡 Planned", "Planned soon")
            return "Planned soon"
        case "missing_phase":
            rewrite(root, "- **Phase:**", "- **Stage:**")
            return "Phase"
        case "screen_elsewhere":
            rewrite(root, screen_link, "../../glossary.md")
            return "glossary.md"
        case "budget_elsewhere":
            rewrite(root, BUDGETS_LINK, "../../specs/technical/01-architecture.md#mono-repo")
            return "01-architecture.md"
        case "empty_budgets":
            rewrite(root, f"- [⏱️ Budgets]({BUDGETS_LINK})\n", "")
            return "Budgets touched"
        case "no_given":
            rewrite(root, "**Given**", "Given")
            return "1"
        case "placeholder":
            rewrite(root, "- Nothing else.", "- {{ID}}")
            return "{{ID}}"
        case "em_dash":
            rewrite(root, "- Nothing else.", f"- Nothing else {EM_DASH} really.")
            return ""
        case _:
            raise ValueError(fault)
