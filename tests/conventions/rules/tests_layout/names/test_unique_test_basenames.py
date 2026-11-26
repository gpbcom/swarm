from __future__ import annotations

# Standard library imports
from pathlib import Path

# First-party imports
from tests.conventions.helpers import write_files
from tests.conventions.rules.tests_layout.names.unique_test_basenames import UniqueTestBasenames


class TestUniqueTestBasenames:
    def test_the_rule_has_its_name(self) -> None:
        assert UniqueTestBasenames.NAME == "unique_test_basenames"

    def test_distinct_names_are_accepted(self, tmp_path: Path) -> None:
        write_files(tmp_path, {"tests/a/test_one.py": "", "tests/b/test_two.py": "", "tests/b/helpers.py": ""})
        assert UniqueTestBasenames().violations(tmp_path) == []

    def test_a_shared_name_is_reported_with_every_file(self, tmp_path: Path) -> None:
        write_files(tmp_path, {"tests/a/test_one.py": "", "tests/b/c/test_one.py": ""})
        found = UniqueTestBasenames().violations(tmp_path)
        assert len(found) == 1
        assert "tests/a/test_one.py" in found[0]
        assert "tests/b/c/test_one.py" in found[0]

    def test_a_cache_folder_is_ignored(self, tmp_path: Path) -> None:
        write_files(tmp_path, {"tests/a/test_one.py": "", "tests/a/__pycache__/test_one.py": ""})
        assert UniqueTestBasenames().violations(tmp_path) == []

    def test_a_root_without_tests_has_no_violation(self, tmp_path: Path) -> None:
        assert UniqueTestBasenames().violations(tmp_path) == []
