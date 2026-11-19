from __future__ import annotations

import tomllib
from typing import ClassVar, Dict, List

import pytest

from tests.conventions.helpers import repo_root


class TestRustSettings:
    NIGHTLY_OPTIONS: ClassVar[List[str]] = [
        "unstable_features",
        "imports_granularity",
        "group_imports",
        "format_code_in_doc_comments",
        "wrap_comments",
        "comment_width",
        "normalize_comments",
        "normalize_doc_attributes",
        "format_strings",
        "format_macro_matchers",
        "format_macro_bodies",
        "struct_field_align_threshold",
        "brace_style",
        "control_brace_style",
        "indent_style",
        "overflow_delimited_expr",
        "reorder_impl_items",
        "version",
    ]

    def load_toml(self, name: str) -> Dict[str, object]:
        path = repo_root() / "packages" / "rust" / name
        assert path.is_file(), f"packages/rust/{name} is missing."
        return tomllib.loads(path.read_text(encoding="utf-8"))

    def workspace(self) -> Dict[str, object]:
        workspace = self.load_toml("Cargo.toml").get("workspace")
        assert isinstance(workspace, dict), "Cargo.toml has no workspace table."
        return workspace

    def lints(self, kind: str) -> Dict[str, object]:
        lints = self.workspace().get("lints")
        assert isinstance(lints, dict), "workspace.lints is missing."
        table = lints.get(kind)
        assert isinstance(table, dict), f"workspace.lints.{kind} is missing."
        return table

    def test_the_rustfmt_file_exists(self) -> None:
        assert self.load_toml("rustfmt.toml") is not None

    def test_the_rustfmt_edition_matches_the_workspace_edition(self) -> None:
        package = self.workspace().get("package")
        assert isinstance(package, dict)
        assert self.load_toml("rustfmt.toml").get("edition") == package.get("edition")

    def test_the_rustfmt_max_width_is_120(self) -> None:
        assert self.load_toml("rustfmt.toml").get("max_width") == 120

    def test_rustfmt_sets_no_option_that_needs_nightly(self) -> None:
        used = [name for name in self.NIGHTLY_OPTIONS if name in self.load_toml("rustfmt.toml")]
        assert used == []

    @pytest.mark.parametrize("name, level", [("all", "deny"), ("pedantic", "warn")])
    def test_the_clippy_levels_and_priorities(self, name: str, level: str) -> None:
        assert self.lints("clippy").get(name) == {"level": level, "priority": -1}

    def test_missing_docs_is_a_warning(self) -> None:
        assert self.lints("rust").get("missing_docs") == "warn"

    def test_the_members_and_the_resolver_are_kept(self) -> None:
        workspace = self.workspace()
        assert "members" in workspace
        assert workspace.get("resolver") == "2"
