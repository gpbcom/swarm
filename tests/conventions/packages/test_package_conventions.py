from __future__ import annotations

from itertools import product
from pathlib import Path
from typing import ClassVar, Dict

import pytest

from tests.conventions.helpers import packages_root, write_files
from tests.conventions.rules.convention_rule import ConventionRule
from tests.conventions.rules.convention_rules import ConventionRules
from tests.conventions.rules.service_tree import ServiceTree


class TestPackageConventions:
    FILES: ClassVar[Dict[str, str]] = {"logging/src/logging_pkg/a.py": ""}

    @pytest.mark.parametrize(
        ("package", "rule"),
        list(product(ServiceTree.discover(packages_root()), ConventionRules.all())),
        ids=[
            f"{package.name}-{rule.NAME}"
            for package, rule in product(ServiceTree.discover(packages_root()), ConventionRules.all())
        ],
    )
    def test_every_rule_holds_for_every_package(self, package: ServiceTree, rule: ConventionRule) -> None:
        violations = rule.violations(package)
        assert violations == [], "\n".join(violations)

    def test_a_package_written_under_a_temporary_root_is_discovered(self, tmp_path: Path) -> None:
        write_files(tmp_path, self.FILES)
        assert [tree.name for tree in ServiceTree.discover(tmp_path)] == ["logging"]
