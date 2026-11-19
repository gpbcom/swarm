from __future__ import annotations

# Standard library imports
import ast
from typing import ClassVar, List, Tuple

# First-party imports
from tests.conventions.rules.convention_rule import ConventionRule
from tests.conventions.rules.service_tree import ServiceTree


class NoAny(ConventionRule):
    """The rule that forbids the ``Any`` type of ``typing``, in ``src/`` and ``tests/``.

    Attributes:
        NAME (str): The short name of the rule.
        MODULES (Tuple[str, ...]): The modules that export the forbidden name.
        FORBIDDEN (str): The forbidden name.

    Notes:
        - An import of the name, aliased or not, is one violation, however many times the name is then used.
        - An attribute access on one of the modules is one violation.
        - Strings and comments never count, because the check reads the syntax tree.
    """

    NAME: ClassVar[str] = "no_any"
    MODULES: ClassVar[Tuple[str, ...]] = ("typing", "typing_extensions")
    FORBIDDEN: ClassVar[str] = "Any"

    ############################
    # Publicly Exposed Methods #
    ############################

    def violations(self, service: ServiceTree) -> List[str]:
        """List the uses of the forbidden type in a service.

        Args:
            service (ServiceTree): The service to check.

        Returns:
            List[str]: One message per import or attribute access, ordered by file then line.
        """
        found: List[str] = []
        for path in service.python_files():
            hits: List[int] = []
            for node in ast.walk(self.parse(path)):
                if isinstance(node, ast.ImportFrom) and node.module in self.MODULES:
                    if any(alias.name == self.FORBIDDEN for alias in node.names):
                        hits.append(node.lineno)
                elif (
                    isinstance(node, ast.Attribute)
                    and node.attr == self.FORBIDDEN
                    and isinstance(node.value, ast.Name)
                    and node.value.id in self.MODULES
                ):
                    hits.append(node.lineno)
            found.extend(
                self.violation(service, path, line, f"The type {self.FORBIDDEN} is forbidden. Use a precise type.")
                for line in sorted(hits)
            )
        return found
