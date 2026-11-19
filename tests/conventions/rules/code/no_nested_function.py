from __future__ import annotations

# Standard library imports
import ast
from typing import ClassVar, List, Tuple

# First-party imports
from tests.conventions.rules.convention_rule import ConventionRule
from tests.conventions.rules.service_tree import ServiceTree


class NoNestedFunction(ConventionRule):
    """No function is defined inside another function.

    Attributes:
        NAME (str): The short name of the rule.

    Notes:
        - A class defined in a function resets the scope, so its methods are not reported.
        - Lambdas never count.
        - Each nested function is reported once, so three levels give two violations.
    """

    NAME: ClassVar[str] = "no_nested_function"

    ############################
    # Internal Helpers Methods #
    ############################

    def _nested(self, tree: ast.Module) -> List[Tuple[int, str]]:
        """Find the functions whose nearest enclosing function or class scope is a function.

        Args:
            tree (ast.Module): The syntax tree to walk.

        Returns:
            List[Tuple[int, str]]: The line and the name of each nested function, sorted by line.
        """
        found: List[Tuple[int, str]] = []
        stack: List[Tuple[ast.AST, bool]] = [(tree, False)]
        while stack:
            node, in_function = stack.pop()
            for child in ast.iter_child_nodes(node):
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if in_function:
                        found.append((child.lineno, child.name))
                    stack.append((child, True))
                elif isinstance(child, ast.ClassDef):
                    stack.append((child, False))
                else:
                    stack.append((child, in_function))
        return sorted(found)

    ############################
    # Publicly Exposed Methods #
    ############################

    def violations(self, service: ServiceTree) -> List[str]:
        """List the nested functions of a service.

        Args:
            service (ServiceTree): The service to check.

        Returns:
            List[str]: One message per nested function, in ``src/`` and ``tests/``.
        """
        messages: List[str] = []
        for path in service.python_files():
            for line, name in self._nested(self.parse(path)):
                messages.append(self.violation(service, path, line, f"Function {name!r} is nested in a function."))
        return messages
