from __future__ import annotations

# Standard library imports
import json
from pathlib import Path

# First-party imports
from tests.harness.tickets.helpers import (
    APPROVED,
    NEXT,
    OTHER_AREA,
    PHASE,
    SAME_AREA,
    lines,
    make_repo,
    open_ticket,
    run,
    write_plan,
)


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
