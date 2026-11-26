from __future__ import annotations

# Standard library imports
import ast
from typing import List, Tuple


class ImportedNames:
    """The absolute dotted names a module imports.

    Notes:
        - A ``from a.b import c`` gives ``a.b.c``, so that ``from swarm_models.config import gateway`` reads as
          ``swarm_models.config.gateway``.
        - Relative imports stay inside their own package, so they give nothing.
    """

    ############################
    # Publicly Exposed Methods #
    ############################

    @classmethod
    def of(cls, tree: ast.Module) -> List[Tuple[int, str]]:
        """List the absolute names imported anywhere in a syntax tree.

        Args:
            tree (ast.Module): The parsed module.

        Returns:
            List[Tuple[int, str]]: The line and the dotted name of each imported target.
        """
        found: List[Tuple[int, str]] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                found.extend((node.lineno, alias.name) for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                for alias in node.names:
                    name = node.module if alias.name == "*" else f"{node.module}.{alias.name}"
                    found.append((node.lineno, name))
        return sorted(found)
