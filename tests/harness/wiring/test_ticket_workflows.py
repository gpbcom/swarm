from __future__ import annotations

import re

import pytest

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

    def test_ticket_run_makes_no_intermediate_commit(self) -> None:
        text = read_text(self.RUN)
        assert "Commit with the message" not in text
        assert "merge ticket/" not in text
        assert "merge feature/" not in text
        for command in ("start", "handoff", "integrate", "status", "prepare", "finish", "diff", "docs"):
            assert f"ticket_tree.py {command}" in text, command

    def test_ticket_run_workers_report_decisions_for_implementation_md(self) -> None:
        text = read_text(self.RUN)
        match = re.search(r"const RESULT =.*?(?=^const )", text, re.DOTALL | re.MULTILINE)
        assert match
        assert "'decisions'" in match.group(0)
        assert "agentType: 'explainer'" in text
        assert "IMPLEMENTATION.md" in text

    @pytest.mark.parametrize("name", ["EXPLAIN.md", "IMPLEMENTATION.md", "REVIEW.md", "TICKET.md"])
    def test_every_ticket_document_has_a_template(self, name: str) -> None:
        assert read_text(f".claude/skills/ticket/templates/{name}")

    def test_the_explain_template_holds_the_generated_changes_table(self) -> None:
        text = read_text(".claude/skills/ticket/templates/EXPLAIN.md")
        assert "<!-- changes -->" in text
        assert "<!-- /changes -->" in text

    def test_the_rules_hold_tkt_14(self) -> None:
        text = read_text(".claude/rules/tickets.md")
        assert "[TKT-14](#tkt-14)" in text
        assert '<a id="tkt-14"></a>' in text

    def test_ticket_run_applies_the_start_rule_at_the_gate(self) -> None:
        text = read_text(self.RUN)
        assert "python3 .claude/scripts/tickets.py check --ticket" in text
        assert "--force" in text

    def test_ticket_run_works_in_the_ticket_s_own_worktree(self) -> None:
        text = read_text(self.RUN)
        assert "home:" in text
        assert "inHome(" in text
        assert text.count("inHome(") >= 8

    def test_ticket_run_moves_the_ticket_on_the_board_and_publishes_it(self) -> None:
        text = read_text(self.RUN)
        assert "board.py move --ticket ${ID} --status running" in text
        assert "pull_request" in text
        assert "feature/${ID}" in text

    def test_ticket_plan_moves_the_ticket_to_planned(self) -> None:
        assert "board.py move --ticket ${ID} --status planned" in read_text(self.PLAN)

    @pytest.mark.parametrize("rule", ["tkt-15", "tkt-16", "tkt-17"])
    def test_the_rules_hold_gitflow_parallel_tickets_and_the_board(self, rule: str) -> None:
        text = read_text(".claude/rules/tickets.md")
        assert f"[{rule.upper()}](#{rule})" in text
        assert f'<a id="{rule}"></a>' in text
