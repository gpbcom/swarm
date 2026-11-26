from __future__ import annotations

# Standard library imports
import json
import subprocess
import sys
from pathlib import Path
from typing import Set

# Third-party imports
import pytest

ROOT = Path(__file__).resolve().parents[3]
REPORTS = ROOT / ".claude" / "scripts" / "reports"
CODE = "import sys; sys.path.insert(0, {reports!r}); import roadmap_gantt as r; import json; print(json.dumps(sorted(r.{call})))"


class TestRoadmapGanttAreas:
    def evaluate(self, call: str) -> Set[str]:
        code = CODE.format(reports=str(REPORTS), call=call)
        output = subprocess.run(
            [sys.executable, "-c", code], cwd=ROOT, capture_output=True, text=True, check=True
        ).stdout
        return set(json.loads(output))

    @pytest.mark.parametrize(
        ("text", "expected"),
        [
            ("backend/apps/gateway", {"backend/apps/gateway"}),
            ("backend/libs/swarm-nats", {"backend/libs/swarm-nats"}),
            ("backend/swarm-models", {"backend/swarm-models"}),
            ("frontend/apps/ground-control", {"frontend/apps/ground-control"}),
            ("frontend/packages/ui", {"frontend/packages/ui"}),
            ("rust/swarm-core", {"rust/swarm-core"}),
            ("infra/charts", {"infra/charts"}),
            ("qa/e2e", {"qa/e2e"}),
        ],
    )
    def test_a_target_layout_folder_is_its_own_area(self, text: str, expected: Set[str]) -> None:
        assert self.evaluate(f"areas({text!r})") == expected

    @pytest.mark.parametrize(
        ("text", "expected"),
        [
            ("services/gateway", {"backend/apps/gateway"}),
            ("packages/python/swarm-models", {"backend/swarm-models"}),
            ("packages/python (lifecycle, logging, catalog)", {"backend/libs"}),
            ("frontends/ground-control", {"frontend/apps/ground-control"}),
            ("packages/ts/live", {"frontend/packages/live"}),
            ("packages/rust (safety)", {"rust"}),
            ("deploy/charts", {"infra/charts"}),
        ],
    )
    def test_a_folder_the_ticket_graph_still_names_is_read_as_its_target_layout_folder(
        self, text: str, expected: Set[str]
    ) -> None:
        assert self.evaluate(f"areas({text!r})") == expected

    @pytest.mark.parametrize(
        ("text", "expected"),
        [
            ("gateway, notifier", {"backend/apps/gateway", "backend/apps/notifier"}),
            ("planner, Mission studio", {"backend/apps/planner", "frontend/apps/mission-studio"}),
            ("mavlink adapter", {"rust"}),
            ("any service or app", {"*"}),
        ],
    )
    def test_a_named_app_or_crate_is_its_target_layout_folder(self, text: str, expected: Set[str]) -> None:
        assert self.evaluate(f"areas({text!r})") == expected
