from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, List

import pytest
from pydantic import JsonValue

from tests.harness.format_edited.helpers import (
    CATALOGUE_RELATIVE,
    make_repo,
    payload_for,
    repo_root,
    run_hook,
)


class TestFormatEdited:
    def test_the_edited_file_is_formatted_and_its_sibling_is_not(self, tmp_path: Path) -> None:
        repo = make_repo(tmp_path / "repo")
        edited = repo / "docs" / "a.txt"
        sibling = repo / "docs" / "b.txt"
        edited.parent.mkdir()
        edited.write_text("hello", encoding="utf-8")
        sibling.write_text("world", encoding="utf-8")
        result = run_hook(payload_for(edited))
        assert result.returncode == 0
        assert result.stdout == ""
        assert edited.read_text(encoding="utf-8") == "HELLO"
        assert sibling.read_text(encoding="utf-8") == "world"

    @pytest.mark.parametrize("tool_name", ["Write", "Edit", "MultiEdit"])
    def test_the_editing_tools_are_handled(self, tmp_path: Path, tool_name: str) -> None:
        repo = make_repo(tmp_path / "repo")
        edited = repo / "a.txt"
        edited.write_text("hello", encoding="utf-8")
        result = run_hook(payload_for(edited, tool_name))
        assert result.returncode == 0
        assert edited.read_text(encoding="utf-8") == "HELLO"

    def test_other_tools_are_ignored(self, tmp_path: Path) -> None:
        repo = make_repo(tmp_path / "repo")
        edited = repo / "a.txt"
        edited.write_text("hello", encoding="utf-8")
        result = run_hook(payload_for(edited, "Read"))
        assert result.returncode == 0
        assert result.stdout == ""
        assert result.stderr == ""
        assert edited.read_text(encoding="utf-8") == "hello"

    def test_a_file_outside_any_git_repository_is_ignored(self, tmp_path: Path) -> None:
        edited = tmp_path / "loose" / "a.txt"
        edited.parent.mkdir()
        edited.write_text("hello", encoding="utf-8")
        result = run_hook(payload_for(edited))
        assert result.returncode == 0
        assert result.stdout == ""
        assert edited.read_text(encoding="utf-8") == "hello"

    def test_a_missing_file_is_ignored(self, tmp_path: Path) -> None:
        repo = make_repo(tmp_path / "repo")
        result = run_hook(payload_for(repo / "ghost.txt"))
        assert result.returncode == 0
        assert result.stdout == ""

    def test_a_file_matching_no_formatter_is_unchanged(self, tmp_path: Path) -> None:
        repo = make_repo(tmp_path / "repo")
        edited = repo / "a.md"
        edited.write_text("hello", encoding="utf-8")
        result = run_hook(payload_for(edited))
        assert result.returncode == 0
        assert result.stdout == ""
        assert edited.read_text(encoding="utf-8") == "hello"

    def test_a_failing_formatter_exits_2_and_names_the_file(self, tmp_path: Path) -> None:
        repo = make_repo(tmp_path / "repo")
        edited = repo / "sub" / "a.bad"
        edited.parent.mkdir()
        edited.write_text("hello", encoding="utf-8")
        result = run_hook(payload_for(edited))
        assert result.returncode == 2
        assert "broken failed on sub/a.bad" in result.stderr

    def test_a_missing_executable_is_not_a_failure(self, tmp_path: Path) -> None:
        repo = make_repo(tmp_path / "repo")
        edited = repo / "a.none"
        edited.write_text("hello", encoding="utf-8")
        result = run_hook(payload_for(edited))
        assert result.returncode == 0
        assert result.stdout == ""

    def test_a_relative_file_path_is_resolved_against_cwd(self, tmp_path: Path) -> None:
        repo = make_repo(tmp_path / "repo")
        edited = repo / "sub" / "a.txt"
        edited.parent.mkdir()
        edited.write_text("hello", encoding="utf-8")
        payload: Dict[str, JsonValue] = {
            "tool_name": "Edit",
            "tool_input": {"file_path": "a.txt"},
            "cwd": str(edited.parent),
        }
        result = run_hook(payload)
        assert result.returncode == 0
        assert edited.read_text(encoding="utf-8") == "HELLO"

    @pytest.mark.parametrize(
        ("path", "expected"),
        [
            ("services/gateway/src/gateway/x.py", ["uv", "run", "ruff", "format", "{file}"]),
            ("tests/a/test_b.py", ["uv", "run", "ruff", "format", "{file}"]),
            ("packages/rust/core/src/lib.rs", ["rustfmt", "--edition", "2021", "{file}"]),
            ("deploy/terraform/cells/dev/main.tf", ["terraform", "fmt", "{file}"]),
        ],
    )
    def test_the_repository_catalogue_picks_the_formatter_of_each_language(
        self, path: str, expected: List[str]
    ) -> None:
        formatters = json.loads((repo_root() / CATALOGUE_RELATIVE).read_text(encoding="utf-8"))["formatters"]
        matching = [item for item in formatters if re.search(item["match"], path)]
        assert matching
        assert matching[0]["run"] == expected

    @pytest.mark.parametrize("path", [".claude/hooks/x.py", "docs/specs/README.md", "frontends/app/src/a.ts"])
    def test_the_repository_catalogue_leaves_other_files_alone(self, path: str) -> None:
        formatters = json.loads((repo_root() / CATALOGUE_RELATIVE).read_text(encoding="utf-8"))["formatters"]
        assert not [item for item in formatters if re.search(item["match"], path)]
