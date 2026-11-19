from __future__ import annotations

from typing import ClassVar, Dict

import pytest

from tests.harness.wiring.helpers import agent_body, agent_files, agent_frontmatter, agent_path, read_text


class TestAgentDefinitions:
    WORKERS = (
        "test-writer",
        "implementer",
        "rust-implementer",
        "frontend-implementer",
        "mockup-writer",
        "doc-writer",
    )

    MODEL_KEY: ClassVar[str] = "model"
    EFFORT_KEY: ClassVar[str] = "effort"

    def tkt7_table(self) -> Dict[str, Dict[str, str]]:
        text = read_text(".claude/rules/tickets.md")
        section = text.split('<a id="tkt-7"></a>', 1)[1].split("\n## ", 1)[0]
        table: Dict[str, Dict[str, str]] = {}
        for line in section.split("\n"):
            if not line.startswith("|"):
                continue
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            if len(cells) < 3 or cells[0] in ("Agent", "---"):
                continue
            for name in cells[0].split(","):
                table[name.strip()] = {self.MODEL_KEY: cells[1], self.EFFORT_KEY: cells[2]}
        return table

    def test_every_agent_names_its_file(self) -> None:
        files = agent_files()
        assert files
        for path in files:
            fields = agent_frontmatter(path)
            assert fields.get("name") == path.stem, path.name
            for key in ("description", "tools", "model", "effort"):
                assert fields.get(key), f"{path.name}: {key}"

    def test_every_agent_has_the_model_and_effort_of_tkt_7(self) -> None:
        table = self.tkt7_table()
        assert table
        for name, expected in table.items():
            fields = agent_frontmatter(agent_path(name))
            assert fields.get("model") == expected[self.MODEL_KEY], name
            assert fields.get("effort") == expected[self.EFFORT_KEY], name

    def test_every_kind_of_task_has_an_agent(self) -> None:
        for name in (*self.WORKERS, "reviewer"):
            assert agent_path(name).is_file(), name

    @pytest.mark.parametrize("name", WORKERS)
    def test_worker_agents_run_in_worktrees_and_know_the_hooks(self, name: str) -> None:
        path = agent_path(name)
        assert agent_frontmatter(path).get("isolation") == "worktree"
        body = agent_body(path)
        assert "format_edited.py" in body
        assert "check_touched.py" in body

    @pytest.mark.parametrize("name", WORKERS)
    def test_worker_agents_hand_off_without_committing(self, name: str) -> None:
        body = agent_body(agent_path(name))
        assert "ticket_tree.py start" in body
        assert "ticket_tree.py handoff" in body
        assert "Never commit" in body
        assert "Commit your changes" not in body
        assert "decision" in body

    def test_the_integrator_never_commits_before_finish(self) -> None:
        body = agent_body(agent_path("integrator"))
        assert "ticket_tree.py integrate" in body
        assert "ticket_tree.py finish" in body
        assert "git merge --no-ff" not in body

    def test_the_explainer_writes_both_documents_from_their_templates(self) -> None:
        path = agent_path("explainer")
        assert path.is_file()
        body = agent_body(path)
        assert ".claude/skills/ticket/templates/EXPLAIN.md" in body
        assert ".claude/skills/ticket/templates/IMPLEMENTATION.md" in body
        assert "ticket_tree.py changes" in body

    def test_the_reviewer_writes_a_review_note_and_stays_read_only(self) -> None:
        path = agent_path("reviewer")
        body = agent_body(path)
        assert "review note" in body
        assert ".claude/skills/ticket/templates/REVIEW.md" in body
        tools = [tool.strip() for tool in agent_frontmatter(path)["tools"].split(",")]
        assert "Write" not in tools
        assert "Edit" not in tools

    def test_the_scribe_writes_the_review_note_file(self) -> None:
        assert "REVIEW.md" in agent_body(agent_path("scribe"))

    def test_the_ticket_writer_uses_the_ticket_template(self) -> None:
        assert ".claude/skills/ticket/templates/TICKET.md" in agent_body(agent_path("ticket-writer"))

    def test_the_verifier_runs_the_ticket_and_plan_checks(self) -> None:
        body = agent_body(agent_path("verifier"))
        assert "check_ticket.py" in body
        assert "check_plan.py" in body
