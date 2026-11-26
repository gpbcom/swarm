from __future__ import annotations

# Standard library imports
import re

# Third-party imports
import pytest

# First-party imports
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

    @pytest.mark.parametrize("workflow", [".claude/workflows/ticket-run.js", ".claude/workflows/ticket-plan.js"])
    def test_a_command_run_exactly_goes_to_the_runner_and_the_exit_code_decides(self, workflow: str) -> None:
        text = read_text(workflow)
        assert "agentType: 'runner'" in text
        assert "exit === expect.exit" in text
        for call in text.split("agentType: 'verifier'")[1:]:
            assert "VERDICT" in call.split("}")[0], "the verifier only runs checks.py and returns a VERDICT"

    def test_the_start_rule_is_run_by_the_runner_never_the_verifier(self) -> None:
        text = read_text(self.RUN)
        step = text.split("const startRule = ", 1)[1].split("if (!startRule", 1)[0]
        assert step.lstrip().startswith("await runExactly(")
        assert "tickets/tickets.py check --ticket" in step
        assert "verifier" not in step

    @pytest.mark.parametrize("path", [PLAN, RUN])
    def test_the_runner_gets_one_command_with_its_folder_as_a_cd_and_never_a_sentence(self, path: str) -> None:
        text = read_text(path)
        assert "async function runExactly(dir, command, expect, opts)" in text
        assert "cd ${JSON.stringify(dir)} && " in text
        assert "work from there" not in text
        assert "From the repository root" not in text

    @pytest.mark.parametrize("path", [PLAN, RUN])
    def test_the_exit_code_is_the_one_the_command_prints(self, path: str) -> None:
        text = read_text(path)
        assert '; echo "${EXIT_MARK}$?"' in text
        assert "const EXIT_MARK = 'SWARM_EXIT_CODE='" in text
        assert "const exit = marked ? Number(marked[1]) : ran.exit_code" in text
        assert "const passed = exit === expect.exit" in text
        assert "ran.output.filter(l => !String(l).includes(EXIT_MARK))" in text

    def test_ticket_run_does_not_hand_the_where_prefix_to_the_runner(self) -> None:
        text = read_text(self.RUN)
        assert "runExactly(WHERE" not in text
        assert "runExactly(HOME, `python3 .claude/scripts/tickets/ticket_tree.py docs" in text
        assert "runExactly('', `python3 .claude/skills/ticket/scripts/check_plan.py" in text

    def test_a_task_blocked_only_by_files_of_later_waves_counts_as_done(self) -> None:
        text = read_text(self.RUN)
        assert "function laterOnly(r, w)" in text
        assert "o.every(t => Number.isInteger(t.wave) && t.wave > w)" in text
        assert "(await runTasks(waveTasks, 'Waves')).map(r => laterOnly(r, w))" in text
        assert "concat(again.map(r => laterOnly(r, w)))" in text
        assert "does not block you" in text

    def test_a_bare_folder_gets_no_owner_and_the_verify_loop_stops_without_one(self) -> None:
        text = read_text(self.RUN)
        assert "if (!/\\.[A-Za-z0-9]+$/.test(f)) return []" in text
        assert "const owned = fixable.filter(f => ownersOf(f).length > 0)" in text
        assert "no failure has an owner" in text
        assert "await fixRound(owned, 'Verify')" in text

    def test_environment_failures_do_not_stop_the_fix_of_the_other_failures(self) -> None:
        text = read_text(self.RUN)
        assert "const fixable = verdict.failures.filter(f => !f.environment)" in text
        assert "if (!fixable.length)" in text
        assert "verdict.failures.some(f => f.environment)) {" not in text

    def test_a_finding_with_several_owners_becomes_one_fix_task_owning_all_their_files(self) -> None:
        text = read_text(self.RUN)
        assert "function mergeTasks(list)" in text
        assert "files: [...new Set(uniq.flatMap(t => t.files))]" in text
        assert "agent: uniq[0].agent" in text
        assert "function groupFixes(items)" in text
        assert "a.files.some(f => b.files.includes(f))" in text
        assert "const groups = groupFixes(items)" in text

    def test_the_reviewer_names_every_file_the_fix_must_change(self) -> None:
        text = read_text(self.RUN)
        assert text.count("name every file the fix must change, tests included") == 2

    def test_findings_on_ticket_md_and_plan_md_go_to_the_ticket_writer_and_the_scribe(self) -> None:
        text = read_text(self.RUN)
        assert "const DOC_OWNERS = { 'TICKET.md': 'ticket-writer', 'PLAN.md': 'scribe' }" in text
        assert "docs\\/tickets\\/[^/]+\\/(TICKET\\.md|PLAN\\.md)$" in text
        assert "const doc = docOwnerOf(item)" in text
        assert "if (doc) return [doc]" in text
        assert "if (g.task.direct)" in text

    def test_the_integrator_puts_the_refused_files_in_blocked_and_the_workflow_logs_them(self) -> None:
        text = read_text(self.RUN)
        assert 'a list "refused"' in text
        assert "Put every entry of it in blocked" in text
        assert "blocked or refused:" in text
