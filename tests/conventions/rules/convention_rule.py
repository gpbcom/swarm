from __future__ import annotations

# Standard library imports
import ast
from abc import ABC, abstractmethod
from pathlib import Path
from typing import ClassVar, List, Optional

# First-party imports
from tests.conventions.rules.service_tree import ServiceTree


class ConventionRule(ABC):
    """A rule of AGENT.md that a test enforces on every service.

    Attributes:
        NAME (str): The short name of the rule, used in test ids and reports.

    Notes:
        A subclass only implements ``violations``. It never needs a change when a service is added.
    """

    NAME: ClassVar[str]

    def __repr__(self) -> str:
        """Return the rule name, so that pytest ids read well.

        Returns:
            str: The value of ``NAME``.
        """
        return self.NAME

    ############################
    # Publicly Exposed Methods #
    ############################

    def parse(self, path: Path) -> ast.Module:
        """Parse a Python file.

        Args:
            path (Path): The file to read as UTF-8.

        Returns:
            ast.Module: The syntax tree, with the path as filename.
        """
        return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))

    def violation(self, service: ServiceTree, path: Path, line: Optional[int], message: str) -> str:
        """Format one violation.

        Args:
            service (ServiceTree): The service the file belongs to.
            path (Path): The offending file.
            line (Optional[int]): The line, or None when the whole file is at fault.
            message (str): What is wrong.

        Returns:
            str: ``<service>/<relative path>:<line>: <message>``, without the line when it is None.
        """
        location = f"{service.name}/{service.relative(path)}"
        if line is not None:
            location = f"{location}:{line}"
        return f"{location}: {message}"

    @abstractmethod
    def violations(self, service: ServiceTree) -> List[str]:
        """List the violations of the rule in a service.

        Args:
            service (ServiceTree): The service to check.

        Returns:
            List[str]: One message per violation, empty when the service complies.
        """
