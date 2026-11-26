from __future__ import annotations

# Third-party imports
import pytest

# First-party imports
from tests.conventions.backend.helpers import backend_root
from tests.conventions.rules.api.api_only_endpoints import ApiOnlyEndpoints
from tests.conventions.rules.command_line.no_command_line import NoCommandLine
from tests.conventions.rules.convention_rule import ConventionRule
from tests.conventions.rules.entities.one_class_per_entity import OneClassPerEntity
from tests.conventions.rules.service_tree import ServiceTree
from tests.conventions.rules.trees.package_tree import PackageTree

RULES = [ApiOnlyEndpoints(), NoCommandLine(), OneClassPerEntity()]


class TestLayoutRules:
    @pytest.mark.parametrize("rule", RULES, ids=[rule.NAME for rule in RULES])
    def test_every_layout_rule_holds_for_the_backend_and_the_scripts(self, rule: ConventionRule) -> None:
        root = backend_root()
        if not PackageTree.discover(root):
            pytest.skip(f"No backend/ or scripts/ folder under {root}.")
        violations = rule.violations(ServiceTree(root))
        assert violations == [], "\n".join(violations)
