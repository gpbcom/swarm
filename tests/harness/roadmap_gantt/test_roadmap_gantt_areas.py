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
            ("backend/apps/gateway", {"services/gateway"}),
            ("backend/libs/swarm-nats", {"packages/python/swarm-nats"}),
            ("frontend/apps/ground-control", {"frontends/ground-control"}),
            ("frontend/packages/ui", {"packages/ts/ui"}),
            ("rust/swarm-core", {"packages/rust/swarm-core"}),
            ("infra/charts", {"deploy/charts"}),
            ("qa/e2e", {"packages/ts/e2e"}),
            ("services/gateway", {"services/gateway"}),
        ],
    )
    def test_both_layouts_name_the_same_area(self, text: str, expected: Set[str]) -> None:
        assert self.evaluate(f"areas({text!r})") == expected

    def test_a_ticket_in_the_new_layout_conflicts_with_one_in_the_old(self) -> None:
        old = self.evaluate("areas('services/gateway')")
        new = self.evaluate("areas('backend/apps/gateway')")
        assert old & new

    @pytest.mark.parametrize("area", ["services/gateway", "backend/apps/gateway"])
    def test_the_alias_table_gives_the_area_in_both_layouts(self, area: str) -> None:
        assert self.evaluate(f"equivalent_areas({area!r})") == {"services/gateway", "backend/apps/gateway"}
