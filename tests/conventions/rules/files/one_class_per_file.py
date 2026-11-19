from __future__ import annotations

# Standard library imports
import ast
from typing import ClassVar, FrozenSet, List

# First-party imports
from tests.conventions.rules.convention_rule import ConventionRule
from tests.conventions.rules.service_tree import ServiceTree


class OneClassPerFile(ConventionRule):
    """Rule: a Python file holds at most one top-level class, whatever the kind of class.

    Attributes:
        NAME (str): The short name of the rule.
        ENUMS_FILE (str): The name of the file that holds all the enums of a module.
        ENUM_BASES (FrozenSet[str]): The base classes that make a class an enum.

    Notes:
        - The rule covers ``src/`` and ``tests/``, and counts Pydantic models, enums, exceptions and helpers alike.
          Nested classes are not counted.
        - **The one exception is ``enums.py``** (AGENT.md, Data and enums): it holds every enum of its module, so it
          may hold several classes, as long as each one is an enum.
    """

    NAME: ClassVar[str] = "one_class_per_file"
    ENUMS_FILE: ClassVar[str] = "enums.py"
    ENUM_BASES: ClassVar[FrozenSet[str]] = frozenset({"Enum", "StrEnum", "IntEnum", "Flag", "IntFlag"})

    ############################
    # Internal Helpers Methods #
    ############################

    def _is_enum(self, node: ast.ClassDef) -> bool:
        """Tell whether a class subclasses one of the enum bases.

        Args:
            node (ast.ClassDef): The class.

        Returns:
            bool: True if one of its bases is named like an enum base, plain or qualified (``enum.StrEnum``).
        """
        names = [
            base.id if isinstance(base, ast.Name) else base.attr
            for base in node.bases
            if isinstance(base, (ast.Name, ast.Attribute))
        ]
        return any(name in self.ENUM_BASES for name in names)

    ############################
    # Publicly Exposed Methods #
    ############################

    def violations(self, service: ServiceTree) -> List[str]:
        """List the files of a service that hold more than one top-level class.

        Args:
            service (ServiceTree): The service to check.

        Returns:
            List[str]: One message per offending file, at the line of its second class.
        """
        found: List[str] = []
        for path in service.python_files():
            classes = [node for node in self.parse(path).body if isinstance(node, ast.ClassDef)]
            if path.name == self.ENUMS_FILE and all(self._is_enum(node) for node in classes):
                continue
            if len(classes) > 1:
                message = f"The file holds {len(classes)} top-level classes. It must hold only one."
                found.append(self.violation(service, path, classes[1].lineno, message))
        return found
