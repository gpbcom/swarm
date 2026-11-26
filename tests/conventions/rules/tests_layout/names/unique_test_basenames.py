from __future__ import annotations

# Standard library imports
from pathlib import Path
from typing import ClassVar, Dict, List

# First-party imports
from tests.conventions.rules.trees.backend_rule import BackendRule
from tests.conventions.rules.trees.package_tree import PackageTree


class UniqueTestBasenames(BackendRule):
    """Rule: two Python test files never share a base name, wherever they sit in ``tests/``.

    Attributes:
        NAME (str): The short name of the rule.
        TEST_PATTERN (str): The glob of a test file.
        CACHE_FOLDER (str): The cache folder that is skipped.

    Notes:
        pytest imports test modules by their base name, so two files with one name collide.
    """

    NAME: ClassVar[str] = "unique_test_basenames"
    TEST_PATTERN: ClassVar[str] = "test_*.py"
    CACHE_FOLDER: ClassVar[str] = "__pycache__"

    ############################
    # Publicly Exposed Methods #
    ############################

    def violations(self, root: Path) -> List[str]:
        """List the test base names that more than one file carries.

        Args:
            root (Path): The repository root.

        Returns:
            List[str]: One message per shared base name, naming every file.
        """
        tests_root = root / PackageTree.TESTS_FOLDER
        if not tests_root.is_dir():
            return []
        names: Dict[str, List[str]] = {}
        for path in sorted(tests_root.rglob(self.TEST_PATTERN)):
            if self.CACHE_FOLDER not in path.parts:
                names.setdefault(path.name, []).append(path.relative_to(root).as_posix())
        return [
            f"{files[0]}: The base name {name} is shared by {', '.join(files)}."
            for name, files in sorted(names.items())
            if len(files) > 1
        ]
