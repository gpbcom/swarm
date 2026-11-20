from __future__ import annotations

import re
from pathlib import Path
from typing import ClassVar, List

import pytest

from tests.conventions.helpers import run_convention_tests
from tests.conventions.rules.convention_rules import ConventionRules
from tests.conventions.rules.service_tree import ServiceTree
from tests.conventions.samples.helpers import write_broken_service


class TestBrokenService:
    NAMES: ClassVar[List[str]] = [
        "one_class_per_file",
        "five_files_per_folder",
        "no_any",
        "no_nested_function",
        "layer_imports",
        "lifecycle_base_classes",
        "pydantic_models_in_models",
        "no_module_docstring",
        "no_logger_argument",
    ]

    def test_the_rules_are_the_nine_of_agent_md(self) -> None:
        assert [rule.NAME for rule in ConventionRules.all()] == self.NAMES

    @pytest.mark.parametrize(
        "name, expected",
        [
            ("one_class_per_file", "two_classes.py"),
            ("five_files_per_folder", "crowded"),
            ("no_any", "typed.py"),
            ("no_nested_function", "nested.py"),
            ("layer_imports", "routes.py"),
            ("lifecycle_base_classes", "job.py"),
            ("pydantic_models_in_models", "customer.py"),
            ("no_module_docstring", "documented.py"),
            ("no_logger_argument", "handing.py"),
        ],
    )
    def test_each_rule_reports_exactly_one_violation(self, tmp_path: Path, name: str, expected: str) -> None:
        service = ServiceTree(write_broken_service(tmp_path / "services"))
        rule = next(rule for rule in ConventionRules.all() if rule.NAME == name)
        violations = rule.violations(service)
        assert len(violations) == 1
        assert expected in violations[0]

    def test_the_convention_tests_fail_once_per_rule(self, tmp_path: Path) -> None:
        services_root = tmp_path / "services"
        write_broken_service(services_root)
        result = run_convention_tests(services_root)
        output = result.stdout + result.stderr
        assert result.returncode != 0
        assert re.search(r"\b9 failed\b", output)
        assert not re.search(r"\b[1-9]\d* passed\b", output)
        for name in self.NAMES:
            assert len(re.findall(rf"FAILED .*\[broken-{name}\]", output)) == 1
