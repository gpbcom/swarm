from __future__ import annotations

# Standard library imports
from pathlib import Path

# First-party imports
from tests.harness.checks.helpers import call


class TestChecksEnvironment:
    def test_a_module_of_the_main_checkout_missing_from_the_clean_tree_is_not_the_environment(
        self, tmp_path: Path
    ) -> None:
        out = "ModuleNotFoundError: No module named 'swarm_service'"
        assert call(f"checks.environment_failure(1, {out!r}, Path({str(tmp_path)!r}))") is False

    def test_a_third_party_module_missing_everywhere_is_the_environment(self, tmp_path: Path) -> None:
        out = "ModuleNotFoundError: No module named 'no_such_third_party_module'"
        assert call(f"checks.environment_failure(1, {out!r}, Path({str(tmp_path)!r}))") is True

    def test_a_missing_command_is_the_environment(self, tmp_path: Path) -> None:
        assert call(f"checks.environment_failure(127, '', Path({str(tmp_path)!r}))") is True
