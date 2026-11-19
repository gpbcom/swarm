from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple

import pytest

from tests.harness.check_ticket.helpers import (
    HEADINGS,
    TICKET_ID,
    apply_fault,
    build_root,
    rewrite,
    script_path,
    swap_headings,
    template_path,
    ticket_file,
)


class TestCheckTicket:
    PREFIX = f"docs/tickets/{TICKET_ID}/TICKET.md: "

    def run_script(self, root: Path, ticket_id: str = TICKET_ID) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(script_path()), ticket_id, "--root", str(root)],
            capture_output=True,
            text=True,
            check=False,
        )

    def test_a_valid_ticket_passes_silently(self, tmp_path: Path) -> None:
        result = self.run_script(build_root(tmp_path))
        assert result.stdout == ""
        assert result.returncode == 0

    @pytest.mark.parametrize(
        "fault",
        [
            "unknown_feature",
            "unknown_use_case",
            "unknown_rule",
            "link_without_id",
            "missing_file",
            "missing_anchor",
            "bad_status",
            "missing_phase",
            "screen_elsewhere",
            "budget_elsewhere",
            "empty_budgets",
            "no_given",
            "placeholder",
            "em_dash",
        ],
    )
    def test_a_ticket_with_a_fault_is_refused_and_the_value_is_named(self, tmp_path: Path, fault: str) -> None:
        root = build_root(tmp_path)
        value = apply_fault(root, fault)
        result = self.run_script(root)
        lines = result.stdout.splitlines()
        assert result.returncode == 1
        assert lines
        assert all(line.startswith(self.PREFIX) for line in lines)
        assert any(value in line for line in lines)

    @pytest.mark.parametrize("heading", HEADINGS)
    def test_a_missing_heading_is_refused(self, tmp_path: Path, heading: str) -> None:
        root = build_root(tmp_path)
        rewrite(root, f"## {heading}\n", "")
        result = self.run_script(root)
        assert result.returncode == 1
        assert any(heading in line for line in result.stdout.splitlines())

    def test_headings_out_of_order_are_refused(self, tmp_path: Path) -> None:
        root = build_root(tmp_path)
        swap_headings(root, "Acceptance criteria", "Out of scope")
        result = self.run_script(root)
        assert result.returncode == 1
        assert any("Out of scope" in line for line in result.stdout.splitlines())

    def test_a_roadmap_page_without_the_ticket_id_is_refused(self, tmp_path: Path) -> None:
        root = build_root(tmp_path, "T9.99")
        result = self.run_script(root, "T9.99")
        assert result.returncode == 1
        assert any("T9.99" in line for line in result.stdout.splitlines())

    def test_a_missing_ticket_file_is_refused(self, tmp_path: Path) -> None:
        root = build_root(tmp_path)
        ticket_file(root).unlink()
        result = self.run_script(root)
        assert result.returncode == 1
        assert TICKET_ID in result.stdout

    @pytest.mark.parametrize("ticket_id", ["T0.3", "0.03", "T00.03", "bad"])
    def test_a_bad_id_gives_usage_and_exit_2(self, tmp_path: Path, ticket_id: str) -> None:
        result = self.run_script(build_root(tmp_path), ticket_id)
        assert result.returncode == 2
        assert "usage" in result.stderr.lower()

    def test_the_template_has_the_nine_headings_in_order(self) -> None:
        text = template_path().read_text(encoding="utf-8")
        found: List[str] = re.findall(r"^## (.+)$", text, flags=re.MULTILINE)
        expected: Tuple[str, ...] = (*HEADINGS, "Assumptions")
        assert tuple(found) == expected
