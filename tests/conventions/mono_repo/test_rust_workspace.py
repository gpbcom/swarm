from __future__ import annotations

# Standard library imports
import tomllib

# First-party imports
from tests.conventions.mono_repo.helpers import repo_root


class TestRustWorkspace:
    def test_the_cargo_workspace_has_members_and_a_resolver(self) -> None:
        path = repo_root() / "rust" / "Cargo.toml"
        assert path.is_file(), "rust/Cargo.toml is missing."
        workspace = tomllib.loads(path.read_text(encoding="utf-8")).get("workspace")
        assert workspace is not None
        assert "members" in workspace
        assert "resolver" in workspace

    def test_the_cargo_lock_file_exists(self) -> None:
        assert (repo_root() / "rust" / "Cargo.lock").is_file()

    def test_there_is_no_cargo_manifest_at_the_root(self) -> None:
        assert not (repo_root() / "Cargo.toml").exists()
