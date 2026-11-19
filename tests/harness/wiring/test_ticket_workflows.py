from __future__ import annotations

import re

from tests.harness.wiring.helpers import phase_titles, read_text


class TestTicketWorkflows:
    PLAN = ".claude/workflows/ticket-plan.js"
    RUN = ".claude/workflows/ticket-run.js"

    def test_ticket_plan_phases(self) -> None:
        assert phase_titles(self.PLAN) == ["Ticket", "Check", "Plan", "Write"]

    def test_ticket_plan_checks_the_ticket_and_the_plan(self) -> None:
        text = read_text(self.PLAN)
        assert ".claude/skills/ticket/scripts/check_ticket.py" in text
        assert ".claude/skills/ticket/scripts/check_plan.py" in text

    def test_ticket_run_phases_are_unchanged(self) -> None:
        assert phase_titles(self.RUN) == ["Gate", "Waves", "Verify", "Review", "Finish"]

    def test_ticket_run_checks_the_plan_at_the_gate(self) -> None:
        assert ".claude/skills/ticket/scripts/check_plan.py" in read_text(self.RUN)

    def test_ticket_run_reviewer_returns_a_note_written_to_review_md(self) -> None:
        text = read_text(self.RUN)
        match = re.search(r"const REVIEW =.*?(?=^const )", text, re.DOTALL | re.MULTILINE)
        assert match
        block = match.group(0)
        assert "note:" in block
        lists = re.findall(r"required:\s*\[([^\]]*)\]", block)
        assert lists
        assert "'note'" in lists[-1]
        assert "REVIEW.md" in text
        assert ".claude/skills/ticket/templates/REVIEW.md" in text
