from __future__ import annotations

# Standard library imports
from itertools import product

# Third-party imports
import pytest

# First-party imports
from tests.conventions.backend.backend_rules import BackendRules
from tests.conventions.backend.helpers import backend_root
from tests.conventions.backend.mirror_tree import MirrorTree
from tests.conventions.rules.convention_rule import ConventionRule
from tests.conventions.rules.convention_rules import ConventionRules
from tests.conventions.rules.service_tree import ServiceTree
from tests.conventions.rules.trees.backend_rule import BackendRule
from tests.conventions.rules.trees.package_tree import PackageTree


class TestBackendConventions:
    @pytest.mark.parametrize("rule", BackendRules.all(), ids=[rule.NAME for rule in BackendRules.all()])
    def test_every_rule_holds_for_the_backend(self, rule: BackendRule) -> None:
        root = backend_root()
        if not PackageTree.discover(root):
            pytest.skip(f"No backend/ or scripts/ folder under {root}.")
        violations = rule.violations(root)
        assert violations == [], "\n".join(violations)

    @pytest.mark.parametrize(
        ("package", "rule"),
        list(product(PackageTree.discover(backend_root()), ConventionRules.all())),
        ids=[
            f"{package.name}-{rule.NAME}"
            for package, rule in product(PackageTree.discover(backend_root()), ConventionRules.all())
        ],
    )
    def test_every_code_rule_holds_for_every_package(self, package: PackageTree, rule: ConventionRule) -> None:
        violations = rule.violations(ServiceTree(package.folder))
        assert violations == [], "\n".join(violations)

    @pytest.mark.parametrize("rule", ConventionRules.all(), ids=[rule.NAME for rule in ConventionRules.all()])
    def test_every_code_rule_holds_for_the_tests_of_the_backend(self, rule: ConventionRule) -> None:
        violations = rule.violations(MirrorTree(backend_root()))
        assert violations == [], "\n".join(violations)
