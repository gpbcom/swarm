from __future__ import annotations

# Standard library imports
import ast
from pathlib import Path
from typing import ClassVar, List

# First-party imports
from tests.conventions.rules.trees.backend_rule import BackendRule
from tests.conventions.rules.trees.package_tree import PackageTree


class NoFileDepthPath(BackendRule):
    """Rule: nothing in ``backend/`` finds a folder by counting the parents of ``__file__``.

    Attributes:
        NAME (str): The short name of the rule.
        PARENTS (str): The attribute that walks up the folders.
        FILE_NAME (str): The name whose use as a starting point is refused.
        CACHE_FOLDER (str): The cache folder that is skipped.
        VENV_FOLDER (str): The virtual environment folder that is skipped.

    Notes:
        ``Path(__file__).parents[3]`` breaks when a file moves. An app passes its own folder instead, through
        ``SWARM_APP_ROOT``.
    """

    NAME: ClassVar[str] = "no_file_depth_path"
    PARENTS: ClassVar[str] = "parents"
    FILE_NAME: ClassVar[str] = "__file__"
    CACHE_FOLDER: ClassVar[str] = "__pycache__"
    VENV_FOLDER: ClassVar[str] = ".venv"

    ############################
    # Internal Helpers Methods #
    ############################

    def _starts_at_file(self, node: ast.expr) -> bool:
        """Tell whether an expression is built from ``__file__``.

        Args:
            node (ast.expr): The expression.

        Returns:
            bool: True when ``__file__`` appears in it.
        """
        return any(isinstance(child, ast.Name) and child.id == self.FILE_NAME for child in ast.walk(node))

    ############################
    # Publicly Exposed Methods #
    ############################

    def violations(self, root: Path) -> List[str]:
        """List the ``__file__`` parent lookups of the backend.

        Args:
            root (Path): The repository root.

        Returns:
            List[str]: One message per ``.parents`` lookup that starts at ``__file__``.
        """
        backend = root / PackageTree.BACKEND_FOLDER
        if not backend.is_dir():
            return []
        found: List[str] = []
        for path in sorted(backend.rglob("*.py")):
            relative = path.relative_to(backend).parts
            if self.CACHE_FOLDER in relative or self.VENV_FOLDER in relative:
                continue
            for node in ast.walk(self.parse(path)):
                if isinstance(node, ast.Attribute) and node.attr == self.PARENTS and self._starts_at_file(node.value):
                    message = "Do not find a folder with the parents of __file__. Pass the folder in."
                    found.append(self.violation(root, path, node.lineno, message))
        return found
