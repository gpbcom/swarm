from __future__ import annotations

# Third-party imports
import pytest

# First-party imports
from tests.conventions.backend.backend_rules import BackendRules
from tests.conventions.backend.helpers import backend_root
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
