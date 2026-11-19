from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

import pytest

from tests.ci.detect_changes.helpers import (
    REPOSITORY_KEY,
    SERVICES_KEY,
    SPECS_KEY,
    TYPESCRIPT_KEY,
    outputs,
    run_detector,
    write_repo,
)

NOTHING: Dict[str, str] = {
    "services": "[]",
    "typescript": "[]",
    "rust": "false",
    "repository": "false",
    "specs": "false",
}


class TestDetectChanges:
    def detect(self, tmp_path: Path, changed: List[str], *args: str) -> Dict[str, str]:
        write_repo(tmp_path)
        result = run_detector(tmp_path, changed, *args)
        assert result.returncode == 0, result.stderr
        return outputs(result)

    def test_the_output_is_five_lines_in_the_contract_order(self, tmp_path: Path) -> None:
        write_repo(tmp_path)
        result = run_detector(tmp_path, ["services/alpha/x.py"])
        keys = [line.split("=", 1)[0] for line in result.stdout.splitlines()]
        assert keys == ["services", "typescript", "rust", "repository", "specs"]
        values = outputs(result)
        assert isinstance(json.loads(values["services"]), list)
        assert isinstance(json.loads(values["typescript"]), list)
        assert {values["rust"], values["repository"], values["specs"]} <= {"true", "false"}

    def test_no_changed_path_selects_nothing(self, tmp_path: Path) -> None:
        assert self.detect(tmp_path, []) == NOTHING

    def test_a_pull_request_touching_one_service_selects_only_that_service(self, tmp_path: Path) -> None:
        changed = [
            "services/alpha/src/alpha/main.py",
            "services/alpha/tests/test_main.py",
            "services/alpha/pyproject.toml",
        ]
        assert self.detect(tmp_path, changed) == {**NOTHING, SERVICES_KEY: '["alpha"]'}

    def test_two_services_are_selected_sorted_and_once_each(self, tmp_path: Path) -> None:
        changed = ["services/beta/a.py", "services/alpha/a.py", "services/beta/b.py"]
        assert self.detect(tmp_path, changed) == {**NOTHING, SERVICES_KEY: '["alpha","beta"]'}

    @pytest.mark.parametrize(
        "path",
        ["services/gone/x.py", "services/_template/x.py", "services/.hidden/x.py", "services/README.md"],
    )
    def test_a_path_of_a_service_that_is_not_discovered_selects_nothing(self, tmp_path: Path, path: str) -> None:
        assert self.detect(tmp_path, [path]) == NOTHING

    def test_a_front_end_with_a_package_is_selected(self, tmp_path: Path) -> None:
        values = self.detect(tmp_path, ["frontends/ground-control/src/main.ts"])
        assert values == {**NOTHING, TYPESCRIPT_KEY: '["frontends/ground-control"]'}

    def test_a_front_end_without_a_package_selects_nothing(self, tmp_path: Path) -> None:
        assert self.detect(tmp_path, ["frontends/notes/x.ts"]) == NOTHING

    @pytest.mark.parametrize("path", ["tests/conventions/x.py", ".claude/hooks/x.py"])
    def test_tests_and_harness_set_only_the_repository_flag(self, tmp_path: Path, path: str) -> None:
        assert self.detect(tmp_path, [path]) == {**NOTHING, REPOSITORY_KEY: "true"}

    def test_specifications_set_only_the_specs_flag(self, tmp_path: Path) -> None:
        assert self.detect(tmp_path, ["docs/specs/glossary.md"]) == {**NOTHING, SPECS_KEY: "true"}

    def test_the_specs_skill_sets_the_specs_and_repository_flags(self, tmp_path: Path) -> None:
        values = self.detect(tmp_path, [".claude/skills/write-specs/scripts/specs.py"])
        assert values == {**NOTHING, SPECS_KEY: "true", REPOSITORY_KEY: "true"}

    @pytest.mark.parametrize(
        "path",
        [
            "docs/tickets/T0.04/TICKET.md",
            "README.md",
            "AGENT.md",
            "deploy/terraform/cells/dev/main.tf",
            ".github/workflows/terraform.yml",
        ],
    )
    def test_unrelated_paths_select_nothing(self, tmp_path: Path, path: str) -> None:
        assert self.detect(tmp_path, [path]) == NOTHING

    def test_blank_lines_and_surrounding_spaces_are_ignored(self, tmp_path: Path) -> None:
        values = self.detect(tmp_path, ["", "  services/alpha/x.py  ", "   ", ""])
        assert values == {**NOTHING, SERVICES_KEY: '["alpha"]'}

    def test_an_unknown_argument_exits_with_two_and_a_usage_line(self, tmp_path: Path) -> None:
        write_repo(tmp_path)
        result = run_detector(tmp_path, [], "--bogus")
        assert result.returncode == 2
        assert "usage" in result.stderr.lower()
