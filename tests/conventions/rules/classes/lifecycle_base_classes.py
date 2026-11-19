from __future__ import annotations

# Standard library imports
import ast
from typing import ClassVar, Dict, List, Set, Tuple

# First-party imports
from tests.conventions.rules.convention_rule import ConventionRule
from tests.conventions.rules.service_tree import ServiceTree


class LifecycleBaseClasses(ConventionRule):
    """Classes outside ``models`` use ``initialize``, ``run`` and ``close`` through a lifecycle base class.

    Attributes:
        NAME (str): The short name of the rule.
        BASES (Tuple[str, ...]): The names of the lifecycle base classes.
        FORBIDDEN (Tuple[str, ...]): The method names no class outside ``models`` may define.

    Notes:
        - The lifecycle classes arrive in a later ticket, so they are recognised by name.
        - A base class is followed through the classes of the same service, so a subclass of a class that is
          itself runnable is accepted.
        - **The visited names are tracked**, so that a cycle of base classes ends instead of looping.
    """

    NAME: ClassVar[str] = "lifecycle_base_classes"
    BASES: ClassVar[Tuple[str, ...]] = ("Runnable", "AsyncRunnable")
    FORBIDDEN: ClassVar[Tuple[str, ...]] = ("start", "stop")

    ############################
    # Internal Helpers Methods #
    ############################

    def _base_name(self, base: ast.expr) -> str:
        """Read the name of a base class expression.

        Args:
            base (ast.expr): One entry of the bases of a class.

        Returns:
            str: The name, the attribute, or the name under a subscript, and an empty string otherwise.
        """
        if isinstance(base, ast.Subscript):
            return self._base_name(base.value)
        if isinstance(base, ast.Attribute):
            return base.attr
        if isinstance(base, ast.Name):
            return base.id
        return ""

    def _collect(self, service: ServiceTree) -> Dict[str, Set[str]]:
        """Collect every class of the service with its base names.

        Args:
            service (ServiceTree): The service to read.

        Returns:
            Dict[str, Set[str]]: The base names of each class name, merged when a name is defined twice.
        """
        classes: Dict[str, Set[str]] = {}
        for path in service.python_files():
            for node in ast.walk(self.parse(path)):
                if isinstance(node, ast.ClassDef):
                    bases = {self._base_name(base) for base in node.bases}
                    classes.setdefault(node.name, set()).update(bases)
        return classes

    def _is_lifecycle(self, name: str, classes: Dict[str, Set[str]]) -> bool:
        """Tell whether a class reaches a lifecycle base class.

        Args:
            name (str): The class name.
            classes (Dict[str, Set[str]]): The base names of every class of the service.

        Returns:
            bool: True when a base resolves, through the service classes, to a name in ``BASES``.
        """
        seen: Set[str] = set()
        pending = [name]
        while pending:
            current = pending.pop()
            if current in seen:
                continue
            seen.add(current)
            for base in classes.get(current, set()):
                if base in self.BASES:
                    return True
                pending.append(base)
        return False

    def _methods(self, node: ast.ClassDef) -> Set[str]:
        """List the methods defined directly in a class body.

        Args:
            node (ast.ClassDef): The class.

        Returns:
            Set[str]: The names of its functions and coroutine functions.
        """
        return {item.name for item in node.body if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))}

    ############################
    # Publicly Exposed Methods #
    ############################

    def violations(self, service: ServiceTree) -> List[str]:
        """List the classes that misuse the lifecycle methods.

        Args:
            service (ServiceTree): The service to check.

        Returns:
            List[str]: One message per class that defines ``start`` or ``stop``, or ``run`` without a lifecycle
                base class, outside the ``models`` layer.
        """
        classes = self._collect(service)
        found: List[str] = []
        for path in service.python_files():
            if service.layer_of(path) == "models":
                continue
            for node in ast.walk(self.parse(path)):
                if not isinstance(node, ast.ClassDef):
                    continue
                methods = self._methods(node)
                forbidden = [name for name in self.FORBIDDEN if name in methods]
                if forbidden:
                    message = f"Class {node.name} defines {', '.join(forbidden)}. Use initialize, run and close."
                elif "run" in methods and not self._is_lifecycle(node.name, classes):
                    message = f"Class {node.name} defines run without a lifecycle base class."
                else:
                    continue
                found.append(self.violation(service, path, node.lineno, message))
        return found
