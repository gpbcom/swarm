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
        assert "python3 .claude/scripts/tickets/tickets.py check --ticket" in text
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
        assert "feature/tickets" in text
        assert "only its own files" in text

    def test_ticket_plan_moves_the_ticket_to_planned(self) -> None:
        assert "board.py move --ticket ${ID} --status planned" in read_text(self.PLAN)

    @pytest.mark.parametrize(
        "rule",
        [
            "tkt-15",
            "tkt-16",
            "tkt-17",
            "tkt-18",
            "tkt-19",
            "tkt-20",
            "tkt-21",
            "tkt-22",
            "tkt-23",
            "tkt-24",
            "tkt-25",
            "tkt-26",
        ],
    )
    def test_the_rules_hold_gitflow_parallel_tickets_and_the_board(self, rule: str) -> None:
        text = read_text(".claude/rules/tickets.md")
        assert f"[{rule.upper()}](#{rule})" in text
        assert f'<a id="{rule}"></a>' in text

    @pytest.mark.parametrize(("skill", "workflow"), [("issue-plan", "ticket-plan"), ("issue-run", "ticket-run")])
    def test_a_group_skill_runs_its_workflow_and_watches_the_group(self, skill: str, workflow: str) -> None:
        text = read_text(f".claude/skills/{skill}/SKILL.md")
        assert f"`{workflow}`" in text
        assert "python3 .claude/scripts/tickets/tickets.py watch <refs> --every 120" in text
        assert "python3 .claude/scripts/tickets/tickets.py resolve <refs>" in text

    def test_only_the_person_approves_a_group(self) -> None:
        text = read_text(".claude/skills/issue-plan/SKILL.md")
        assert "Never run `tickets.py approve` on your own initiative" in text

    def test_the_readme_explains_how_to_run_tickets_and_groups(self) -> None:
        text = read_text("README.md")
        assert "## 🎫 Working on tickets" in text
        for command in ("/ticket-run", "/issue-plan", "/issue-run", "tickets.py approve", "tickets.py prune"):
            assert command in text

    @pytest.mark.parametrize("agent", ["planner", "mockup-writer", "reviewer", "frontend-implementer"])
    def test_the_agents_that_build_and_check_screens_know_tkt_21(self, agent: str) -> None:
        assert "TKT-21" in read_text(f".claude/agents/{agent}.md")

    def test_the_ticket_template_asks_a_front_end_ticket_for_its_screens(self) -> None:
        text = read_text(".claude/skills/ticket/templates/TICKET.md")
        assert "➖ No screen" in text
        assert "TKT-21" in text

    def test_ticket_plan_and_ticket_run_refuse_a_ticket_already_done(self) -> None:
        assert "python3 .claude/scripts/tickets/tickets.py done --ticket" in read_text(self.PLAN)
        assert "python3 .claude/scripts/tickets/tickets.py check --ticket" in read_text(self.RUN)
        assert "already done" in read_text(self.RUN)
