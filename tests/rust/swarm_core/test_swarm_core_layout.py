from __future__ import annotations

# Standard library imports
import tomllib
from fnmatch import fnmatch
from pathlib import Path
from typing import ClassVar, Dict, List, Tuple

# Third-party imports
import pytest


class TestSwarmCoreLayout:
    ROOT: ClassVar[Path] = Path(__file__).resolve().parents[3]
    WORKSPACE: ClassVar[Path] = ROOT / "packages" / "rust"
    CORE: ClassVar[Path] = WORKSPACE / "swarm-core"
    PYTHON: ClassVar[Path] = CORE / "python"
    CRATES: ClassVar[List[Tuple[str, str, str]]] = [
        ("safety", "swarm-core-safety", "tick"),
        ("planner", "swarm-core-planner", "plan"),
        ("mavlink", "swarm-core-mavlink", "encode"),
    ]
    STUB_FUNCTIONS: ClassVar[List[str]] = ["safety_tick", "planner_plan", "mavlink_encode"]
    BINDING_DEPENDENCIES: ClassVar[List[str]] = [
        "pyo3",
        "swarm-core-safety",
        "swarm-core-planner",
        "swarm-core-mavlink",
    ]

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

    @pytest.mark.parametrize(("folder", "package", "bench"), CRATES)
    def test_the_crate_is_a_member_of_the_workspace(self, folder: str, package: str, bench: str) -> None:
        manifest = self._load(self.WORKSPACE / "Cargo.toml")
        assert f"swarm-core/{folder}" in self._members(manifest)

    def test_the_workspace_keeps_resolver_two(self) -> None:
        manifest = self._load(self.WORKSPACE / "Cargo.toml")
        assert self._table(manifest, "workspace")["resolver"] == "2"

    @pytest.mark.parametrize(("folder", "package", "bench"), CRATES)
    def test_the_crate_manifest_follows_the_workspace(self, folder: str, package: str, bench: str) -> None:
        manifest = self._load(self.CORE / folder / "Cargo.toml")
        crate = self._table(manifest, "package")
        assert crate["name"] == package
        assert crate["publish"] is False
        assert crate["edition"] == {"workspace": True}
        assert manifest["lints"] == {"workspace": True}

    @pytest.mark.parametrize(("folder", "package", "bench"), CRATES)
    def test_the_crate_has_a_library_source(self, folder: str, package: str, bench: str) -> None:
        assert (self.CORE / folder / "src" / "lib.rs").is_file()

    @pytest.mark.parametrize(("folder", "package", "bench"), CRATES)
    def test_the_crate_depends_on_criterion_for_development(self, folder: str, package: str, bench: str) -> None:
        manifest = self._load(self.CORE / folder / "Cargo.toml")
        assert "criterion" in self._table(manifest, "dev-dependencies")

    @pytest.mark.parametrize(("folder", "package", "bench"), CRATES)
    def test_the_crate_declares_its_benchmark_without_the_default_harness(
        self, folder: str, package: str, bench: str
    ) -> None:
        manifest = self._load(self.CORE / folder / "Cargo.toml")
        benches = manifest["bench"]
        assert isinstance(benches, list)
        matching = [entry for entry in benches if isinstance(entry, dict) and entry.get("name") == bench]
        assert len(matching) == 1
        assert matching[0]["harness"] is False
        assert (self.CORE / folder / "benches" / f"{bench}.rs").is_file()

    def test_the_bindings_crate_is_a_member_of_the_workspace(self) -> None:
        manifest = self._load(self.WORKSPACE / "Cargo.toml")
        assert "swarm-core/python" in self._members(manifest)

    def test_the_bindings_crate_builds_the_swarm_core_library(self) -> None:
        manifest = self._load(self.PYTHON / "Cargo.toml")
        library = self._table(manifest, "lib")
        assert self._table(manifest, "package")["name"] == "swarm-core-python"
        assert manifest["lints"] == {"workspace": True}
        assert library["name"] == "swarm_core"
        assert "cdylib" in library["crate-type"]  # type: ignore[operator]

    @pytest.mark.parametrize("dependency", BINDING_DEPENDENCIES)
    def test_the_bindings_crate_depends_on_its_crates(self, dependency: str) -> None:
        manifest = self._load(self.PYTHON / "Cargo.toml")
        assert dependency in self._table(manifest, "dependencies")

    def test_the_bindings_python_project_is_built_by_maturin(self) -> None:
        manifest = self._load(self.PYTHON / "pyproject.toml")
        build = self._table(manifest, "build-system")
        project = self._table(manifest, "project")
        maturin = self._table(self._table(manifest, "tool"), "maturin")
        requires = build["requires"]
        assert isinstance(requires, list)
        assert build["build-backend"] == "maturin"
        assert any(str(entry).startswith("maturin") for entry in requires)
        assert project["name"] == "swarm-core"
        assert project["requires-python"] == ">=3.12"
        assert maturin["module-name"] == "swarm_core"

    @pytest.mark.parametrize("function", STUB_FUNCTIONS)
    def test_the_bindings_type_stub_declares_the_function(self, function: str) -> None:
        stub = self.PYTHON / "swarm_core.pyi"
        assert stub.is_file()
        assert f"def {function}" in stub.read_text(encoding="utf-8")

    def test_the_bindings_folder_is_outside_the_uv_workspace(self) -> None:
        root = self._load(self.ROOT / "pyproject.toml")
        members = self._table(self._table(self._table(root, "tool"), "uv"), "workspace")["members"]
        assert isinstance(members, list)
        relative = self.PYTHON.relative_to(self.ROOT).as_posix()
        assert not any(fnmatch(relative, str(pattern)) for pattern in members)
