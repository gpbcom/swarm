from __future__ import annotations

# Standard library imports
import tomllib
from fnmatch import fnmatch
from pathlib import Path
from typing import ClassVar, Dict, List


class TestSyntheticDronesLayout:
    ROOT: ClassVar[Path] = Path(__file__).resolve().parents[3]
    WORKSPACE: ClassVar[Path] = ROOT / "rust"
    CRATE: ClassVar[Path] = WORKSPACE / "swarm-synthetic-drones"
    PACKAGE: ClassVar[str] = "swarm-synthetic-drones"
    BENCH: ClassVar[str] = "step"

    ############################
    # Internal Helpers Methods #
    ############################

    def _load(self, path: Path) -> Dict[str, object]:
        assert path.is_file(), f"{path} does not exist."
        with path.open("rb") as handle:
            return tomllib.load(handle)

    def _table(self, manifest: Dict[str, object], key: str) -> Dict[str, object]:
        table = manifest[key]
        assert isinstance(table, dict)
        return table

    def _members(self, manifest: Dict[str, object]) -> List[str]:
        members = self._table(manifest, "workspace")["members"]
        assert isinstance(members, list)
        return [str(member) for member in members]

    ############################
    # Publicly Exposed Methods #
    ############################

    def test_the_crate_is_a_member_of_the_workspace(self) -> None:
        manifest = self._load(self.WORKSPACE / "Cargo.toml")
        assert self.PACKAGE in self._members(manifest)

    def test_the_crate_manifest_follows_the_workspace(self) -> None:
        manifest = self._load(self.CRATE / "Cargo.toml")
        crate = self._table(manifest, "package")
        assert crate["name"] == self.PACKAGE
        assert crate["edition"] == {"workspace": True}
        assert manifest["lints"] == {"workspace": True}

    def test_the_crate_depends_on_mavlink(self) -> None:
        manifest = self._load(self.CRATE / "Cargo.toml")
        assert "mavlink" in self._table(manifest, "dependencies")

    def test_the_crate_declares_its_benchmark_without_the_default_harness(self) -> None:
        manifest = self._load(self.CRATE / "Cargo.toml")
        benches = manifest["bench"]
        assert isinstance(benches, list)
        matching = [entry for entry in benches if isinstance(entry, dict) and entry.get("name") == self.BENCH]
        assert len(matching) == 1
        assert matching[0]["harness"] is False
        assert (self.CRATE / "benches" / f"{self.BENCH}.rs").is_file()

    def test_the_crate_has_a_binary_source(self) -> None:
        assert (self.CRATE / "src" / "main.rs").is_file()

    def test_the_crate_folder_is_outside_the_uv_workspace(self) -> None:
        root = self._load(self.ROOT / "pyproject.toml")
        members = self._table(self._table(self._table(root, "tool"), "uv"), "workspace")["members"]
        assert isinstance(members, list)
        relative = self.CRATE.relative_to(self.ROOT).as_posix()
        assert not any(fnmatch(relative, str(pattern)) for pattern in members)
