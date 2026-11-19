from __future__ import annotations

import shutil
from pathlib import Path
from typing import List

import pytest

from tests.conventions.helpers import repo_root, run_convention_tests
from tests.conventions.rules.convention_rules import ConventionRules
from tests.conventions.rules.service_tree import ServiceTree


class TestEmptyService:
    @pytest.fixture(params=["skeleton", "bare"])
    def root(self, request: pytest.FixtureRequest, tmp_path: Path) -> Path:
        services = tmp_path / "services"
        shutil.copytree(
            repo_root() / "services" / "gateway",
            services / "gateway",
            ignore=shutil.ignore_patterns("__pycache__"),
        )
        empty = services / "empty"
        empty.mkdir()
        (empty / "pyproject.toml").write_text('[project]\nname = "empty"\nversion = "0.1.0"\n', encoding="utf-8")
        if request.param == "skeleton":
            package = empty / "src" / "empty"
            package.mkdir(parents=True)
            (package / "__init__.py").write_text("", encoding="utf-8")
            for layer in ["api", "service", "storage", "clients", "models"]:
                (package / layer).mkdir()
                (package / layer / "__init__.py").write_text("", encoding="utf-8")
            (empty / "tests").mkdir()
        return services

    def test_discovery_finds_both_services(self, root: Path) -> None:
        names = sorted(service.name for service in ServiceTree.discover(root))
        assert names == ["empty", "gateway"]

    def test_every_rule_holds_for_the_empty_service(self, root: Path) -> None:
        empty = next(service for service in ServiceTree.discover(root) if service.name == "empty")
        violations: List[str] = []
        for rule in ConventionRules.all():
            violations.extend(rule.violations(empty))
        assert violations == []

    def test_the_convention_tests_pass_unchanged(self, root: Path) -> None:
        result = run_convention_tests(root)
        assert result.returncode == 0, result.stdout + result.stderr
        assert "14 passed" in result.stdout
        assert "failed" not in result.stdout

    def test_no_convention_test_names_the_empty_service(self) -> None:
        folder = repo_root() / "tests" / "conventions"
        for path in folder.rglob("*.py"):
            if path.name == "test_empty_service.py":
                continue
            assert '"empty"' not in path.read_text(encoding="utf-8"), str(path)
