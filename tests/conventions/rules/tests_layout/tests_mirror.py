from __future__ import annotations

# Standard library imports
from pathlib import Path
from typing import ClassVar, Dict, List

# First-party imports
from tests.conventions.rules.trees.backend_rule import BackendRule
from tests.conventions.rules.trees.package_tree import PackageTree


class TestsMirror(BackendRule):
    """Rule: ``tests/swarm_<module>/...`` mirrors the import path of the package it tests.

    Attributes:
        NAME (str): The short name of the rule.
        TEST_PREFIX (str): The prefix of a test file name.
        SUFFIX (str): The suffix of a Python file.

    Notes:
        - A test folder matches a folder of the module, or a source file of the module: the folder
          ``customer_service/`` holds the several test classes of ``customer_service.py``.
        - A ``test_<subject>.py`` file matches ``<subject>.py`` or the package ``<subject>/`` beside it.
        - Other files (``helpers.py``, ``conftest.py``) and the folders that do not start with ``swarm_`` are free.
    """

    NAME: ClassVar[str] = "tests_mirror"
    TEST_PREFIX: ClassVar[str] = "test_"
    SUFFIX: ClassVar[str] = ".py"

    ############################
    # Internal Helpers Methods #
    ############################

    def _check(self, root: Path, path: Path, module_dir: Path, parts: List[str]) -> List[str]:
        """Walk the folders of a test file down the module.

        Args:
            root (Path): The repository root.
            path (Path): The test file.
            module_dir (Path): The folder of the module.
            parts (List[str]): The folders between the module's test folder and the file, then the file name.

        Returns:
            List[str]: The violations of the file.
        """
        current = module_dir
        for folder in parts[:-1]:
            if (current / folder).is_dir():
                current = current / folder
            elif (current / f"{folder}{self.SUFFIX}").is_file():
                return []
            else:
                message = f"The folder {folder} has no counterpart in {current.relative_to(root).as_posix()}."
                return [self.violation(root, path, None, message)]
        name = parts[-1]
        if not name.startswith(self.TEST_PREFIX) or not name.endswith(self.SUFFIX):
            return []
        subject = name[len(self.TEST_PREFIX) : -len(self.SUFFIX)]
        if (current / f"{subject}{self.SUFFIX}").is_file() or (current / subject).is_dir():
            return []
        message = f"No {subject}{self.SUFFIX} in {current.relative_to(root).as_posix()} for this test."
        return [self.violation(root, path, None, message)]

    ############################
    # Publicly Exposed Methods #
    ############################

    def violations(self, root: Path) -> List[str]:
        """List the test files and folders that do not mirror a package.

        Args:
            root (Path): The repository root.

        Returns:
            List[str]: One message per test file without its counterpart in the module.
        """
        packages = PackageTree.discover(root)
        modules: Dict[str, Path] = {package.module: package.module_dir for package in packages}
        tests_root = root / PackageTree.TESTS_FOLDER
        if not tests_root.is_dir():
            return []
        found: List[str] = []
        for path in sorted(tests_root.rglob(f"*{self.SUFFIX}")):
            parts = list(path.relative_to(tests_root).parts)
            if parts[0] == "__pycache__" or "__pycache__" in parts or not parts[0].startswith(PackageTree.PREFIX):
                continue
            if len(parts) == 1:
                continue
            if parts[0] not in modules:
                message = f"The folder {parts[0]} mirrors no package of the backend."
                found.append(self.violation(root, path, None, message))
                continue
            found.extend(self._check(root, path, modules[parts[0]], parts[1:]))
        return found
