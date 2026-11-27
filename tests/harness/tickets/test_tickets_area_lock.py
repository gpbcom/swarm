from __future__ import annotations

# Standard library imports
import json
from pathlib import Path

# Third-party imports
import pytest

# First-party imports
from tests.harness.tickets.helpers import (
    APPROVED,
    NEXT,
    OTHER_AREA,
    PHASE,
    SAME_AREA,
    add_ticket_to_graph,
    lines,
    make_repo,
    open_ticket,
    run,
    write_plan,
    write_plan_with_tasks,
)

LOCK_FILE = "pnpm-lock.yaml"
CATALOGUE = "frontend/packages/i18n/src/messages/en.json"
THIRD = "T9.05"


class TestTicketsAreaLock:
    def test_an_open_ticket_continuing_its_run_passes_the_area_lock_of_a_ticket_admitted_with_it(
        self, tmp_path: Path
    ) -> None:
        main = make_repo(tmp_path)
        open_ticket(main, NEXT)
        open_ticket(main, SAME_AREA)
        for ticket in (NEXT, SAME_AREA):
            result = run(main, "check", "--ticket", ticket)
            assert result.returncode == 0, result.stdout
            assert result.stdout == ""

    def test_an_open_ticket_still_waits_for_its_prerequisites(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        open_ticket(main, OTHER_AREA)
        result = run(main, "check", "--ticket", OTHER_AREA)
        assert result.returncode == 1
        assert NEXT in result.stdout
        assert "area lock" not in result.stdout

    def test_next_never_returns_two_tickets_whose_areas_overlap(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        write_plan(main, NEXT, APPROVED)
        write_plan(main, SAME_AREA, APPROVED)
        order = [row["ticket"] for row in json.loads(run(main, "resolve", PHASE, "--json").stdout)]
        first = min((NEXT, SAME_AREA), key=order.index)
        assert lines(run(main, "next", PHASE)) == [first]

    @pytest.mark.parametrize("shared", [LOCK_FILE, CATALOGUE, "uv.lock", "rust/Cargo.lock"])
    def test_a_ticket_waits_while_another_open_ticket_s_plan_lists_one_of_its_shared_files(
        self, tmp_path: Path, shared: str
    ) -> None:
        main = make_repo(tmp_path)
        write_plan_with_tasks(main, OTHER_AREA, APPROVED, [("K01", ["rust/a.rs", shared])])
        open_ticket(main, OTHER_AREA)
        write_plan_with_tasks(main, NEXT, APPROVED, [("K01", ["backend/apps/missions/a.py", shared])])
        result = run(main, "check", "--ticket", NEXT)
        assert result.returncode == 1
        assert OTHER_AREA in result.stdout
        assert shared in result.stdout
        assert "shared file lock" in result.stdout

    def test_a_shared_file_another_open_ticket_already_owns_makes_the_ticket_wait(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        open_ticket(main, OTHER_AREA, paths=[f"docs/tickets/{OTHER_AREA}/", LOCK_FILE])
        write_plan_with_tasks(main, NEXT, APPROVED, [("K01", [LOCK_FILE])])
        result = run(main, "check", "--ticket", NEXT)
        assert result.returncode == 1
        assert LOCK_FILE in result.stdout

    def test_tickets_whose_plans_list_different_shared_files_start_together(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        write_plan_with_tasks(main, OTHER_AREA, APPROVED, [("K01", ["uv.lock", "rust/a.rs"])])
        open_ticket(main, OTHER_AREA)
        write_plan_with_tasks(main, NEXT, APPROVED, [("K01", [LOCK_FILE, "frontend/apps/x/package.json"])])
        result = run(main, "check", "--ticket", NEXT)
        assert result.returncode == 0, result.stdout
        assert result.stdout == ""

    def test_next_never_starts_two_tickets_whose_plans_list_one_shared_file(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        add_ticket_to_graph(main, THIRD, "frontend/apps/ground-control")
        write_plan_with_tasks(main, NEXT, APPROVED, [("K01", [CATALOGUE])])
        write_plan_with_tasks(main, THIRD, APPROVED, [("K01", [CATALOGUE])])
        result = run(main, "next", NEXT, THIRD)
        assert lines(result) == [NEXT]
        assert CATALOGUE in result.stderr
