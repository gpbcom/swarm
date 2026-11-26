from __future__ import annotations

# Standard library imports
import json
import os
import subprocess
import sys
from pathlib import Path

# Third-party imports
import pytest

# First-party imports
from tests.harness.check_ticket.helpers import build_root, repo_root, rewrite, script_path

TICKET = "T0.16"
GRAPH_RELATIVE = "gantt/ticket-graph.json"


class TestCheckTicketFrontEnd:
    def root_with_area(self, tmp_path: Path, area: str) -> Path:
        root = build_root(tmp_path, TICKET)
        specs = root / "docs" / "specs"
        specs.unlink()
        specs.mkdir()
        real = repo_root() / "docs" / "specs"
        for entry in real.iterdir():
            if entry.name != "roadmap":
                os.symlink(entry, specs / entry.name)
        (specs / "roadmap" / "gantt").mkdir(parents=True)
        for entry in (real / "roadmap").iterdir():
            if entry.name != "gantt":
                os.symlink(entry, specs / "roadmap" / entry.name)
        graph = {"tickets": {TICKET: {"area": area}}}
        (specs / "roadmap" / GRAPH_RELATIVE).write_text(json.dumps(graph), encoding="utf-8")
        rewrite(root, "- [Screen](../../specs/screens/UC-001/a1.png)\n", "", TICKET)
        return root

    def run_script(self, root: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(script_path()), TICKET, "--root", str(root)],
            capture_output=True,
            text=True,
            check=False,
        )

    def test_a_front_end_ticket_must_list_its_screens(self, tmp_path: Path) -> None:
        result = self.run_script(self.root_with_area(tmp_path, "frontend/apps/ground-control"))
        assert result.returncode == 1
        assert "TKT-21" in result.stdout

    @pytest.mark.parametrize("area", ["backend/apps/gateway", "backend/swarm-service", "frontend/packages/ui"])
    def test_a_ticket_that_changes_no_front_end_app_needs_no_screen(self, tmp_path: Path, area: str) -> None:
        result = self.run_script(self.root_with_area(tmp_path, area))
        assert "TKT-21" not in result.stdout
