from __future__ import annotations

# Standard library imports
import ast
from abc import ABC, abstractmethod
from pathlib import Path
from typing import ClassVar, List, Optional


class BackendRule(ABC):
    """A rule of AGENT.md that a test enforces on the backend layout of a repository.

    Attributes:
        NAME (str): The short name of the rule, used in test ids and reports.

    Notes:
        A subclass only implements ``violations``. It has the shape of ``ConventionRule``, but it checks a whole
        repository root, because its rules cross package boundaries.
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

    def violation(self, root: Path, path: Path, line: Optional[int], message: str) -> str:
        """Format one violation.

        Args:
            root (Path): The repository root.
            path (Path): The offending file or folder.
            line (Optional[int]): The line, or None when the whole path is at fault.
            message (str): What is wrong.

        Returns:
            str: ``<relative path>:<line>: <message>``, without the line when it is None.
        """
        location = path.relative_to(root).as_posix()
        if line is not None:
            location = f"{location}:{line}"
        return f"{location}: {message}"

    @abstractmethod
    def violations(self, root: Path) -> List[str]:
        """List the violations of the rule in a repository.

        Args:
            root (Path): The repository root, holding ``backend/``, ``scripts/`` and ``tests/``.

        Returns:
            List[str]: One message per violation, empty when the repository complies.
        """
