from __future__ import annotations

# Standard library imports
import json
from pathlib import Path
from typing import List

# Third-party imports
import pytest

# First-party imports
from tests.harness.tickets.helpers import (
    APPROVED,
    AWAITING,
    DONE,
    EPIC,
    FIELD,
    ISSUES,
    NEXT,
    OTHER_AREA,
    PHASE,
    SAME_AREA,
    finish_on_shared_branch,
    lines,
    make_repo,
    open_ticket,
    run,
    write_plan,
)


def resolved_closed(main: Path, closed: str, *refs: str) -> List[str]:
    result = run(main, "resolve", "--json", *refs, closed=closed)
    assert result.returncode == 0, result.stderr
    return [row["ticket"] for row in json.loads(result.stdout)]


def resolved(main: Path, *refs: str) -> List[str]:
    result = run(main, "resolve", "--json", *refs)
    assert result.returncode == 0, result.stderr
    return [row["ticket"] for row in json.loads(result.stdout)]


class TestGroups:
    @pytest.mark.parametrize(
        ("refs", "expected"),
        [
            ([f"#{ISSUES[NEXT]}"], [NEXT]),
            ([f"#{ISSUES[EPIC]}"], [NEXT, OTHER_AREA]),
            ([f"#{ISSUES[PHASE]}"], [NEXT, SAME_AREA, OTHER_AREA]),
            ([EPIC], [NEXT, OTHER_AREA]),
            ([PHASE], [NEXT, SAME_AREA, OTHER_AREA]),
            ([OTHER_AREA, NEXT], [NEXT, OTHER_AREA]),
            ([f"#{ISSUES[NEXT]}", FIELD], [NEXT, FIELD]),
        ],
    )
    def test_a_group_resolves_to_its_tickets_in_the_order_of_their_prerequisites(
        self, tmp_path: Path, refs: List[str], expected: List[str]
    ) -> None:
        assert resolved(make_repo(tmp_path), *refs) == expected

    def test_a_merged_ticket_is_left_out(self, tmp_path: Path) -> None:
        assert DONE not in resolved(make_repo(tmp_path), f"#{ISSUES[EPIC]}")

    def test_an_unknown_reference_is_refused(self, tmp_path: Path) -> None:
        result = run(make_repo(tmp_path), "resolve", "#999")
        assert result.returncode == 1
        assert "#999" in result.stderr

    def test_a_group_whose_tickets_are_all_done_does_nothing(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        result = run(main, "resolve", DONE)
        assert result.returncode == 0
        assert "nothing to do" in result.stdout
        assert lines(run(main, "next", DONE)) == []
        report = run(main, "watch", DONE, "--once").stdout
        assert "Every ticket of the group is merged" in report

    def test_an_issue_closed_on_github_counts_as_done(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        closed = f"{ISSUES[NEXT]},{ISSUES[SAME_AREA]}"
        assert resolved_closed(main, closed, f"#{ISSUES[PHASE]}") == [OTHER_AREA]

    def test_next_never_starts_a_ticket_running_in_review_or_merged(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        for ticket in (NEXT, SAME_AREA, OTHER_AREA):
            write_plan(main, ticket, APPROVED)
        open_ticket(main, SAME_AREA)
        finish_on_shared_branch(main, NEXT)
        assert lines(run(main, "next", PHASE)) == [OTHER_AREA]

    def test_plans_already_approved_or_of_finished_tickets_are_left_alone(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        approved = write_plan(main, NEXT, APPROVED)
        finished = write_plan(main, OTHER_AREA, AWAITING)
        finish_on_shared_branch(main, OTHER_AREA)
        before = approved.read_text(encoding="utf-8")
        assert run(main, "approve", EPIC).returncode == 0
        assert approved.read_text(encoding="utf-8") == before
        assert AWAITING in finished.read_text(encoding="utf-8")

    def test_a_done_ticket_is_never_run_again_even_forced(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        for args in (["check", "--ticket", DONE], ["check", "--ticket", DONE, "--force"]):
            result = run(main, *args)
            assert result.returncode == 1
            assert "already done" in result.stdout

    def test_a_ticket_closed_on_github_is_never_run_again(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        result = run(main, "check", "--ticket", NEXT, "--force", closed=str(ISSUES[NEXT]))
        assert result.returncode == 1
        assert "already done" in result.stdout

    def test_a_finished_ticket_is_never_run_again_even_forced(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        finish_on_shared_branch(main, NEXT)
        result = run(main, "check", "--ticket", NEXT, "--force")
        assert result.returncode == 1
        assert "already finished" in result.stdout

    @pytest.mark.parametrize(("ticket", "closed", "expected"), [(DONE, "", 0), (NEXT, "", 1), (NEXT, "4", 0)])
    def test_done_tells_whether_a_ticket_needs_no_more_work(
        self, tmp_path: Path, ticket: str, closed: str, expected: int
    ) -> None:
        result = run(make_repo(tmp_path), "done", "--ticket", ticket, closed=closed)
        assert result.returncode == expected
        assert (result.stdout != "") == (expected == 0)

    def test_resolve_shows_each_ticket_s_state(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        write_plan(main, NEXT, AWAITING)
        shown = "\n".join(lines(run(main, "resolve", EPIC)))
        assert "awaits approval" in shown
        assert "no plan" in shown

    def test_approve_approves_every_plan_of_the_group_that_awaits_it(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        first = write_plan(main, NEXT, AWAITING)
        second = write_plan(main, OTHER_AREA, AWAITING)
        result = run(main, "approve", EPIC)
        assert result.returncode == 0, result.stderr
        for plan in (first, second):
            assert APPROVED in plan.read_text(encoding="utf-8")
            progress = (plan.parent / "PROGRESS.md").read_text(encoding="utf-8")
            assert "Plan approved by the person (group approval)" in progress

    def test_approve_leaves_a_plan_that_fails_its_check(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        plan = write_plan(main, NEXT, AWAITING)
        result = run(main, "approve", NEXT, check_plan="false")
        assert result.returncode == 1
        assert AWAITING in plan.read_text(encoding="utf-8")

    def test_next_lists_the_approved_tickets_that_may_start(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        write_plan(main, NEXT, APPROVED)
        write_plan(main, OTHER_AREA, APPROVED)
        write_plan(main, SAME_AREA, AWAITING)
        assert lines(run(main, "next", PHASE)) == [NEXT]

    def test_next_holds_a_ticket_back_while_another_changes_its_area(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        write_plan(main, SAME_AREA, APPROVED)
        open_ticket(main, NEXT)
        assert lines(run(main, "next", SAME_AREA)) == []

    def test_watch_once_reports_every_ticket_and_what_can_start(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        write_plan(main, NEXT, APPROVED)
        write_plan(main, SAME_AREA, AWAITING)
        report = run(main, "watch", PHASE, "--once").stdout
        for ticket in (NEXT, SAME_AREA, OTHER_AREA):
            assert ticket in report
        assert f"▶️ CAN START {NEXT}" in report
