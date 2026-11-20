from __future__ import annotations

# Standard library imports
from pathlib import Path
from typing import ClassVar, Dict, Optional

# Third-party imports
import pytest

# First-party imports
from tests.conventions.helpers import write_files
from tests.conventions.rules.service_tree import ServiceTree


class TestServiceTree:
    THREE_SERVICES: ClassVar[Dict[str, str]] = {
        "zeta/src/zeta/a.py": "",
        "alpha/src/alpha/a.py": "",
        "mid/src/mid/a.py": "",
    }
    HIDDEN_AND_PRIVATE: ClassVar[Dict[str, str]] = {".hidden/a.py": "", "_private/a.py": "", "real/src/real/a.py": ""}
    WITH_A_FILE: ClassVar[Dict[str, str]] = {"README.md": "", "real/src/real/a.py": ""}
    SOURCES_AND_TESTS: ClassVar[Dict[str, str]] = {
        "svc/src/svc/b.py": "",
        "svc/src/svc/a.py": "",
        "svc/tests/test_a.py": "",
        "svc/src/svc/notes.txt": "",
    }
    WITH_CACHE_AND_HIDDEN: ClassVar[Dict[str, str]] = {
        "svc/src/svc/__pycache__/a.py": "",
        "svc/src/svc/.hidden/a.py": "",
        "svc/src/svc/a.py": "",
    }

    def test_discovery_is_sorted_by_name(self, tmp_path: Path) -> None:
        write_files(tmp_path, self.THREE_SERVICES)
        assert [tree.name for tree in ServiceTree.discover(tmp_path)] == ["alpha", "mid", "zeta"]

    def test_discovery_skips_hidden_and_underscore_folders(self, tmp_path: Path) -> None:
        write_files(tmp_path, self.HIDDEN_AND_PRIVATE)
        assert [tree.name for tree in ServiceTree.discover(tmp_path)] == ["real"]

    def test_discovery_ignores_files(self, tmp_path: Path) -> None:
        write_files(tmp_path, self.WITH_A_FILE)
        assert [tree.name for tree in ServiceTree.discover(tmp_path)] == ["real"]

    def test_discovery_of_a_missing_root_is_empty(self, tmp_path: Path) -> None:
        assert ServiceTree.discover(tmp_path / "missing") == []

    def test_roots_and_name(self, tmp_path: Path) -> None:
        tree = ServiceTree(tmp_path / "gateway")
        assert tree.name == "gateway"
        assert tree.source_root == tmp_path / "gateway" / "src"
        assert tree.tests_root == tmp_path / "gateway" / "tests"

    def test_layers(self) -> None:
        assert ServiceTree.LAYERS == ("api", "service", "storage", "clients", "models")

    def test_python_files_cover_src_and_tests_sorted(self, tmp_path: Path) -> None:
        write_files(tmp_path, self.SOURCES_AND_TESTS)
        tree = ServiceTree(tmp_path / "svc")
        assert [tree.relative(path) for path in tree.python_files()] == [
            "src/svc/a.py",
            "src/svc/b.py",
            "tests/test_a.py",
        ]

    def test_python_files_skip_pycache_and_hidden_folders(self, tmp_path: Path) -> None:
        write_files(tmp_path, self.WITH_CACHE_AND_HIDDEN)
        tree = ServiceTree(tmp_path / "svc")
        assert [tree.relative(path) for path in tree.python_files()] == ["src/svc/a.py"]

    def test_python_files_of_a_service_without_folders_are_empty(self, tmp_path: Path) -> None:
        (tmp_path / "svc").mkdir()
        assert ServiceTree(tmp_path / "svc").python_files() == []

    @pytest.mark.parametrize("layer", ["api", "service", "storage", "clients", "models"])
    def test_layer_of_a_file_in_each_layer(self, tmp_path: Path, layer: str) -> None:
        tree = ServiceTree(tmp_path / "svc")
        assert tree.layer_of(tree.source_root / "svc" / layer / "a.py") == layer

    @pytest.mark.parametrize(
        "relative",
        ["src/svc/a.py", "src/svc/other/a.py", "tests/api/test_a.py", "src/a.py"],
    )
    def test_layer_of_a_file_outside_a_layer_is_none(self, tmp_path: Path, relative: str) -> None:
        tree = ServiceTree(tmp_path / "svc")
        assert tree.layer_of(tmp_path / "svc" / relative) is None

    @pytest.mark.parametrize(
        ("relative", "expected"),
        [("src/svc/api/a.py", "svc"), ("src/svc/a.py", "svc"), ("tests/a.py", None)],
    )
    def test_package_of(self, tmp_path: Path, relative: str, expected: Optional[str]) -> None:
        tree = ServiceTree(tmp_path / "svc")
        assert tree.package_of(tmp_path / "svc" / relative) == expected

    def test_relative_is_a_posix_path_from_the_service_root(self, tmp_path: Path) -> None:
        tree = ServiceTree(tmp_path / "svc")
        assert tree.relative(tmp_path / "svc" / "src" / "svc" / "a.py") == "src/svc/a.py"
