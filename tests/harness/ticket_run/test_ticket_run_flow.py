from __future__ import annotations

# Standard library imports
from pathlib import Path

# First-party imports
from tests.harness.ticket_run.helpers import (
    DONE,
    TICKET,
    blocked,
    failing,
    labels,
    prompts,
    rule,
    run_workflow,
    task,
)

TEST_FILE = "tests/swarm_service/test_a.py"
CHART_LOCK = "infra/charts/cell/Chart.lock"
UNOWNED = "frontend/packages/live/src/live-worker-core.ts"


class TestTicketRunFlow:
    def test_a_blocker_no_task_owns_stops_the_wave_at_once_with_the_plan_change(self, tmp_path: Path) -> None:
        tasks = [task("K01", ["frontend/packages/live/src/tracing/frame_tracing.ts"], agent="frontend-implementer")]
        run = run_workflow(tmp_path, tasks, [rule(blocked(UNOWNED, "wire traceSquadFrame"), label="K01 ")])
        assert labels(run).count("K01 frontend-implementer") == 1
        result = run["result"]
        assert isinstance(result, dict)
        assert "L-57" in str(result["stopped"])
        assert f"add {UNOWNED} to the files of K01" in str(result["next"])
        [stop] = prompts(run, f"record the stop {TICKET}")
        assert "ticket_tree.py stop --ticket T9.07" in stop

    def test_a_file_a_fixer_reports_goes_to_its_owner_before_the_next_verification(self, tmp_path: Path) -> None:
        tasks = [task("K01", [TEST_FILE], agent="test-writer"), task("K37", [CHART_LOCK])]
        rules = [
            rule(failing(TEST_FILE), label="verifier round 1", times=1),
            rule(blocked(CHART_LOCK, "the digest does not match Chart.yaml"), label="K01 test-writer (fix)"),
        ]
        run = run_workflow(tmp_path, tasks, rules)
        order = labels(run)
        assert "K37 implementer (fix)" in order
        assert order.index("K01 test-writer (fix)") < order.index("K37 implementer (fix)")
        assert order.index("K37 implementer (fix)") < order.index("verifier round 2")
        [fix] = prompts(run, "K37 implementer (fix)")
        assert "the digest does not match Chart.yaml" in fix

    def test_the_images_are_verified_in_a_second_call_whose_failures_count(self, tmp_path: Path) -> None:
        tasks = [task("K01", ["frontend/apps/ground-control/src/map.tsx"], agent="frontend-implementer")]
        rules = [rule(failing("frontend/apps/ground-control/src/map.tsx"), label="verifier round 1 (images)", times=1)]
        run = run_workflow(tmp_path, tasks, rules)
        [images] = prompts(run, "verifier round 1 (images)")
        assert f"checks.py --ticket {TICKET} --images" in images
        assert "timeout set to 600000 ms" in images
        assert "K01 frontend-implementer (fix)" in labels(run)
        assert "verifier round 2" in labels(run)

    def test_a_run_that_ends_with_failing_checks_records_its_stop(self, tmp_path: Path) -> None:
        tasks = [task("K01", [TEST_FILE], agent="test-writer")]
        run = run_workflow(
            tmp_path, tasks, [rule(failing(TEST_FILE), agent_type="verifier", prompt="checks.py --ticket T9.07,")]
        )
        result = run["result"]
        assert isinstance(result, dict)
        assert result["done"] is False
        [stop] = prompts(run, f"record the stop {TICKET}")
        assert "check failure(s) left after the fix rounds" in stop

    def test_a_run_that_completes_records_no_stop(self, tmp_path: Path) -> None:
        run = run_workflow(tmp_path, [task("K01", [TEST_FILE], agent="test-writer")], [rule(DONE, label="K01 ")])
        result = run["result"]
        assert isinstance(result, dict)
        assert result["awaitingReview"] is True
        assert not prompts(run, "record the stop")
