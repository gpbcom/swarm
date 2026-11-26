from __future__ import annotations

# Standard library imports
import json
from pathlib import Path
from typing import List

# First-party imports
from tests.harness.ticket_tree.helpers import (
    OTHER,
    SHARED_BRANCH,
    TICKET,
    add_ticket,
    commit_count,
    documents_problems,
    make_repo,
    run,
    state_path,
)

SHARED_FILE = "shared.txt"


def share_file(main: Path, tickets: List[str]) -> None:
    """Write one file and record it as owned by every ticket of ``tickets``, as two tickets that change one file do."""
    (main / SHARED_FILE).write_text("shared\n", encoding="utf-8")
    for ticket in tickets:
        path = state_path(main, ticket)
        state = json.loads(path.read_text(encoding="utf-8"))
        state["paths"] = sorted({*state.get("paths", []), SHARED_FILE})
        path.write_text(json.dumps(state), encoding="utf-8")


class TestTicketTreeFinishDocuments:
    def test_finish_rewrites_a_changes_table_another_ticket_s_commit_made_stale(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        add_ticket(main, OTHER)
        assert run(main, "prepare").returncode == 0
        assert run(main, "prepare", ticket=OTHER).returncode == 0
        share_file(main, [TICKET, OTHER])
        assert documents_problems(main, "", "") == ""
        assert run(main, "changes", "--write", ticket=OTHER).returncode == 0
        assert run(main, "finish", "--no-pull-request").returncode == 0
        assert run(main, "changes", "--check", ticket=OTHER).returncode == 1
        second = run(main, "finish", "--no-pull-request", ticket=OTHER)
        assert second.returncode == 0, second.stderr
        assert commit_count(main, SHARED_BRANCH) == 3

    def test_finish_still_refuses_a_document_with_a_broken_link(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        assert run(main, "prepare").returncode == 0
        share_file(main, [TICKET])
        documents_problems(main, "See [gone](../../../missing.py).", "")
        result = run(main, "finish", "--no-pull-request")
        assert result.returncode == 1
        assert "does not exist" in result.stderr
        assert commit_count(main, SHARED_BRANCH) == 1
