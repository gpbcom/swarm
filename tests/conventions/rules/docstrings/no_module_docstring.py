from __future__ import annotations

# Standard library imports
import ast
from typing import ClassVar, List

# First-party imports
from tests.conventions.rules.convention_rule import ConventionRule
from tests.conventions.rules.service_tree import ServiceTree


class NoModuleDocstring(ConventionRule):
    """No Python file starts with a docstring.

    Attributes:
        NAME (str): The short name of the rule.

    Notes:
        - A file holds one class, and the docstring of that class says what the file is for (AGENT.md, Docstrings and
          comments).
        - ``__init__.py`` files and console scripts count like any other file.
    """

    NAME: ClassVar[str] = "no_module_docstring"

    ############################
    # Publicly Exposed Methods #
    ############################

    def violations(self, service: ServiceTree) -> List[str]:
        """List the files of a service that start with a docstring.

        Args:
            service (ServiceTree): The service to check.

        Returns:
            List[str]: One message per file with a module docstring, in ``src/`` and ``tests/``.
        """
        messages: List[str] = []
        for path in service.python_files():
            tree = self.parse(path)
            if ast.get_docstring(tree, clean=False) is not None:
                messages.append(self.violation(service, path, tree.body[0].lineno, "The file starts with a docstring."))
        return messages
