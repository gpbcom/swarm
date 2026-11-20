from __future__ import annotations

# Standard library imports
from itertools import product

# Third-party imports
import pytest

# First-party imports
from tests.conventions.helpers import services_root
from tests.conventions.rules.convention_rule import ConventionRule
from tests.conventions.rules.convention_rules import ConventionRules
from tests.conventions.rules.service_tree import ServiceTree


class TestServiceConventions:
    @pytest.mark.parametrize(
        ("service", "rule"),
        list(product(ServiceTree.discover(services_root()), ConventionRules.all())),
        ids=[
            f"{service.name}-{rule.NAME}"
            for service, rule in product(ServiceTree.discover(services_root()), ConventionRules.all())
        ],
    )
    def test_every_rule_holds_for_every_service(self, service: ServiceTree, rule: ConventionRule) -> None:
        violations = rule.violations(service)
        assert violations == [], "\n".join(violations)
