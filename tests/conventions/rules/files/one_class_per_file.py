from __future__ import annotations

# Standard library imports
import ast
from typing import ClassVar, List

# First-party imports
from tests.conventions.rules.convention_rule import ConventionRule
from tests.conventions.rules.service_tree import ServiceTree


class OneClassPerFile(ConventionRule):
    """Rule: a Python file holds at most one top-level class, whatever the kind of class.

    Attributes:
        NAME (str): The short name of the rule.

    Notes:
        The rule covers ``src/`` and ``tests/``, and counts Pydantic models, enums, exceptions and helpers alike.
        Nested classes are not counted.
    """

    NAME: ClassVar[str] = "one_class_per_file"

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
            if len(classes) > 1:
                message = f"The file holds {len(classes)} top-level classes. It must hold only one."
                found.append(self.violation(service, path, classes[1].lineno, message))
        return found
