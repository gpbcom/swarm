from __future__ import annotations

# Standard library imports
from pathlib import Path
from typing import ClassVar, List, Tuple

# First-party imports
from tests.conventions.rules.service_tree import ServiceTree
from tests.conventions.rules.trees.package_tree import PackageTree


class MirrorTree(ServiceTree):
    """The central tests of the backend, as the convention rules walk them: the mirrors, the scripts and the fakes.

    Attributes:
        FOLDERS (ClassVar[Tuple[str, ...]]): The folders of ``tests/`` checked besides the ``swarm_*`` mirrors.
        CACHE_FOLDER (ClassVar[str]): The cache folder that is skipped.

    Notes:
        - The root is the repository root: ``src`` is absent, so a rule that checks only the sources finds nothing.
        - The tests of every package sit in one central tree, so the rules that the services and packages ran on
          their own ``tests/`` folders run here.
    """

    FOLDERS: ClassVar[Tuple[str, ...]] = ("scripts", "fakes")
    CACHE_FOLDER: ClassVar[str] = "__pycache__"

    ############################
    # Publicly Exposed Methods #
    ############################

    def python_files(self) -> List[Path]:
        """List the Python files of the tests of the backend.

        Returns:
            List[Path]: Every ``*.py`` file under ``tests/swarm_*``, ``tests/scripts`` and ``tests/fakes``, sorted.
        """
        tests = self.root / PackageTree.TESTS_FOLDER
        if not tests.is_dir():
            return []
        files: List[Path] = []
        for folder in sorted(tests.iterdir()):
            if folder.is_dir() and (folder.name.startswith(PackageTree.PREFIX) or folder.name in self.FOLDERS):
                files.extend(path for path in folder.rglob("*.py") if self.CACHE_FOLDER not in path.parts)
        return sorted(files)
