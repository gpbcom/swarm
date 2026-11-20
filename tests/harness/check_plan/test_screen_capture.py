from __future__ import annotations

# Standard library imports
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Third-party imports
from pydantic import JsonValue

# First-party imports
from tests.harness.check_plan.helpers import APPROVED, a_task, repo_root, script_path

FRONT_END = "T0.16"
BACK_END = "T0.03"
SCREEN_LIGHT = "docs/specs/screens/UC-029/a1.png"
SCREEN_DARK = "docs/specs/screens/UC-029/a1.dark.png"
USE_CASE_PAGE = "docs/specs/functional/use-cases/UC-029-create-an-operator.md"
SCREENS = "- [🖼️ UC-029 A1](../../specs/functional/use-cases/UC-029-create-an-operator.md#screen-a1)"


def ticket_root(tmp_path: Path, ticket: str, screens: str = SCREENS) -> Path:
    root = tmp_path / "root"
    (root / "docs" / "tickets" / ticket).mkdir(parents=True)
    os.symlink(repo_root() / "docs" / "specs", root / "docs" / "specs")
    text = f"# {ticket}: Sample\n\n## Screens touched\n\n{screens}\n\n## Budgets touched\n\n- None.\n"
    (root / "docs" / "tickets" / ticket / "TICKET.md").write_text(text, encoding="utf-8")
    return root


def capture(depends_on: List[str], files: Optional[List[str]] = None) -> Dict[str, JsonValue]:
    return a_task("K03", "mockup-writer", 3, depends_on, files or [SCREEN_LIGHT, SCREEN_DARK, USE_CASE_PAGE])


def plan(root: Path, ticket: str, tasks: List[Dict[str, JsonValue]]) -> subprocess.CompletedProcess[str]:
    text = f"# {ticket}: Plan\n\n{APPROVED}\n\n## Task graph\n\n```json\n{json.dumps(tasks)}\n```\n"
    (root / "docs" / "tickets" / ticket / "PLAN.md").write_text(text, encoding="utf-8")
    return subprocess.run(
        [sys.executable, str(script_path()), ticket, "--root", str(root)],
        capture_output=True,
        text=True,
        check=False,
    )


def front_end_work() -> List[Dict[str, JsonValue]]:
    return [
        a_task("K01", "test-writer", 1, files=["frontends/back-office/e2e/operator.spec.ts"]),
        a_task("K02", "frontend-implementer", 2, ["K01"], ["frontends/back-office/src/operator.tsx"]),
    ]


class TestScreenCapture:
    def test_a_front_end_plan_captures_every_screen_after_the_front_end_work(self, tmp_path: Path) -> None:
        result = plan(ticket_root(tmp_path, FRONT_END), FRONT_END, [*front_end_work(), capture(["K02"])])
        assert result.stdout == "", result.stdout

    def test_a_front_end_plan_without_a_capture_task_is_refused(self, tmp_path: Path) -> None:
        result = plan(ticket_root(tmp_path, FRONT_END), FRONT_END, front_end_work())
        assert result.returncode == 1
        assert "TKT-21" in result.stdout
        assert "UC-029 a1" in result.stdout

    def test_a_capture_that_does_not_wait_for_the_front_end_work_is_refused(self, tmp_path: Path) -> None:
        tasks = [*front_end_work(), capture(["K01"])]
        tasks[2]["wave"] = 2
        result = plan(ticket_root(tmp_path, FRONT_END), FRONT_END, tasks)
        assert result.returncode == 1
        assert "K02" in result.stdout

    def test_a_capture_must_own_the_dark_screen_too(self, tmp_path: Path) -> None:
        tasks = [*front_end_work(), capture(["K02"], [SCREEN_LIGHT, USE_CASE_PAGE])]
        result = plan(ticket_root(tmp_path, FRONT_END), FRONT_END, tasks)
        assert result.returncode == 1
        assert SCREEN_DARK in result.stdout

    def test_a_ticket_with_no_screen_needs_no_capture(self, tmp_path: Path) -> None:
        root = ticket_root(tmp_path, FRONT_END, "- ➖ No screen: the shells hold no state of a use case yet.")
        assert plan(root, FRONT_END, front_end_work()).stdout == ""

    def test_a_ticket_that_changes_no_front_end_needs_no_capture(self, tmp_path: Path) -> None:
        tasks = [a_task("K01", "test-writer", 1), a_task("K02", "implementer", 2, ["K01"])]
        assert plan(ticket_root(tmp_path, BACK_END), BACK_END, tasks).stdout == ""
