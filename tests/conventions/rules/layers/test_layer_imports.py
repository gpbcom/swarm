from __future__ import annotations

# Standard library imports
from pathlib import Path
from typing import ClassVar, Dict, List, Tuple

# Third-party imports
import pytest

# First-party imports
from tests.conventions.helpers import write_files
from tests.conventions.rules.layers.layer_imports import LayerImports
from tests.conventions.rules.service_tree import ServiceTree


class TestLayerImports:
    ALLOWED: ClassVar[List[Tuple[str, str]]] = [
        ("api", "api"),
        ("api", "service"),
        ("api", "models"),
        ("service", "service"),
        ("service", "storage"),
        ("service", "clients"),
        ("service", "models"),
        ("storage", "storage"),
        ("storage", "models"),
        ("clients", "clients"),
        ("clients", "models"),
        ("models", "models"),
    ]
    REFUSED: ClassVar[List[Tuple[str, str]]] = [
        ("api", "storage"),
        ("api", "clients"),
        ("service", "api"),
        ("storage", "api"),
        ("storage", "service"),
        ("storage", "clients"),
        ("clients", "api"),
        ("clients", "service"),
        ("clients", "storage"),
        ("models", "api"),
        ("models", "service"),
        ("models", "storage"),
        ("models", "clients"),
    ]

    MODULE_PATH: ClassVar[str] = "src/sample/{source}/module.py"
    PACKAGE_IMPORT: ClassVar[str] = "from sample.{target}.thing import Thing\n"
    BARE_IMPORT: ClassVar[str] = "from {target}.thing import Thing\n"
    PLAIN_IMPORT: ClassVar[Dict[str, str]] = {"src/sample/api/module.py": "import sample.storage.store\n"}
    RELATIVE_UP: ClassVar[Dict[str, str]] = {"src/sample/api/routes.py": "from ..storage.store import Store\n"}
    RELATIVE_SAME: ClassVar[Dict[str, str]] = {"src/sample/api/routes.py": "from .helpers import Helper\n"}
    FROM_PACKAGE: ClassVar[Dict[str, str]] = {"src/sample/api/routes.py": "from sample import storage\n"}
    ROUTES_PATH: ClassVar[str] = "src/sample/api/routes.py"
    TEST_FILE: ClassVar[Dict[str, str]] = {"tests/api/test_routes.py": "from sample.storage.store import Store\n"}
    PACKAGE_INIT: ClassVar[Dict[str, str]] = {"src/sample/__init__.py": "from sample.storage.store import Store\n"}
    STANDARD_LIBRARY: ClassVar[Dict[str, str]] = {"src/sample/api/routes.py": "import os\nfrom pathlib import Path\n"}
    THIRD_PARTY: ClassVar[Dict[str, str]] = {"src/sample/models/item.py": "from pydantic import BaseModel\n"}
    NO_SOURCES: ClassVar[Dict[str, str]] = {"pyproject.toml": ""}

    def violations_of(self, tmp_path: Path, files: Dict[str, str]) -> List[str]:
        write_files(tmp_path / "services" / "sample", files)
        service = ServiceTree(tmp_path / "services" / "sample")
        return LayerImports().violations(service)

    def test_the_rule_is_named_layer_imports(self) -> None:
        assert LayerImports.NAME == "layer_imports"

    def test_every_pair_is_covered(self) -> None:
        assert len(self.ALLOWED) + len(self.REFUSED) == 25
        assert len(set(self.ALLOWED + self.REFUSED)) == 25

    @pytest.mark.parametrize(("source", "target"), ALLOWED)
    def test_an_allowed_import_is_not_a_violation(self, tmp_path: Path, source: str, target: str) -> None:
        files = {
            self.MODULE_PATH.format(source=source): self.PACKAGE_IMPORT.format(target=target),
        }
        assert self.violations_of(tmp_path, files) == []

    @pytest.mark.parametrize(("source", "target"), REFUSED)
    def test_a_refused_import_is_one_violation(self, tmp_path: Path, source: str, target: str) -> None:
        files = {
            self.MODULE_PATH.format(source=source): self.PACKAGE_IMPORT.format(target=target),
        }
        found = self.violations_of(tmp_path, files)
        assert len(found) == 1
        assert found[0].startswith(f"sample/src/sample/{source}/module.py:1: ")

    @pytest.mark.parametrize(("source", "target"), ALLOWED + REFUSED)
    def test_a_bare_layer_import_is_judged_like_a_package_import(
        self, tmp_path: Path, source: str, target: str
    ) -> None:
        files = {self.MODULE_PATH.format(source=source): self.BARE_IMPORT.format(target=target)}
        expected = 0 if (source, target) in self.ALLOWED else 1
        assert len(self.violations_of(tmp_path, files)) == expected

    def test_a_plain_import_statement_is_checked(self, tmp_path: Path) -> None:
        files = self.PLAIN_IMPORT
        assert len(self.violations_of(tmp_path, files)) == 1

    def test_a_relative_import_is_resolved_from_the_package(self, tmp_path: Path) -> None:
        files = self.RELATIVE_UP
        found = self.violations_of(tmp_path, files)
        assert len(found) == 1
        assert found[0].startswith("sample/src/sample/api/routes.py:1: ")

    def test_a_relative_import_inside_the_layer_is_allowed(self, tmp_path: Path) -> None:
        files = self.RELATIVE_SAME
        assert self.violations_of(tmp_path, files) == []

    def test_importing_a_layer_from_the_package_is_refused(self, tmp_path: Path) -> None:
        files = self.FROM_PACKAGE
        assert len(self.violations_of(tmp_path, files)) == 1

    def test_an_import_under_type_checking_is_checked(self, tmp_path: Path) -> None:
        source = "from typing import TYPE_CHECKING\n\nif TYPE_CHECKING:\n    from sample.storage.store import Store\n"
        found = self.violations_of(tmp_path, {self.ROUTES_PATH: source})
        assert len(found) == 1
        assert ":4: " in found[0]

    def test_a_test_file_may_import_any_layer(self, tmp_path: Path) -> None:
        files = self.TEST_FILE
        assert self.violations_of(tmp_path, files) == []

    def test_a_file_directly_in_the_package_is_not_checked(self, tmp_path: Path) -> None:
        files = self.PACKAGE_INIT
        assert self.violations_of(tmp_path, files) == []

    def test_a_standard_library_import_is_ignored(self, tmp_path: Path) -> None:
        files = self.STANDARD_LIBRARY
        assert self.violations_of(tmp_path, files) == []

    def test_a_third_party_import_is_ignored(self, tmp_path: Path) -> None:
        files = self.THIRD_PARTY
        assert self.violations_of(tmp_path, files) == []

    def test_two_refused_imports_in_one_file_are_two_violations(self, tmp_path: Path) -> None:
        source = "from sample.storage.store import Store\nfrom sample.clients.remote import Remote\n"
        assert len(self.violations_of(tmp_path, {self.ROUTES_PATH: source})) == 2

    def test_a_service_without_sources_has_no_violation(self, tmp_path: Path) -> None:
        assert self.violations_of(tmp_path, self.NO_SOURCES) == []
