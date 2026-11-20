from __future__ import annotations

# Standard library imports
from pathlib import Path
from typing import List

# First-party imports
from tests.conventions.helpers import repo_root
from tests.conventions.rules.imports.import_sections import ImportSections


class TestRootImportSections:
    def test_every_module_of_the_root_tests_folder_has_its_import_sections(self) -> None:
        rule = ImportSections()
        root = repo_root()
        first_party = rule.first_party(root, set())
        problems: List[str] = []
        for path in sorted((root / "tests").rglob("*.py")):
            if "__pycache__" in path.parts:
                continue
            for line, message in rule.problems(path, first_party):
                problems.append(f"{Path(path).relative_to(root)}:{line}: {message}")
        assert problems == []
