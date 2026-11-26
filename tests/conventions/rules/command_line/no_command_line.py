from __future__ import annotations

# Standard library imports
import ast
import os
from pathlib import Path
from typing import ClassVar, List, Set, Tuple

# First-party imports
from tests.conventions.rules.convention_rule import ConventionRule
from tests.conventions.rules.service_tree import ServiceTree


class NoCommandLine(ConventionRule):
    """The product has no command line: no parser, no ``sys.argv``, no ``cli`` or ``commands`` module.

    Attributes:
        NAME (str): The short name of the rule.
        ROOTS (Tuple[str, ...]): The folders checked, under the tree root.
        TEST_ROOT (str): The folder of the mirrored tests.
        TEST_MIRRORS (Tuple[str, ...]): The names, or name prefixes ending with ``_``, of the tests checked.
        SKIPPED (Tuple[str, ...]): The folders never entered.
        PARSERS (Set[str]): The modules that build a command line.
        FORBIDDEN_NAMES (Set[str]): The folder and module names refused.
        SYS (str): The module that holds ``argv``.
        ARGV (str): The command line attribute.

    Notes:
        The tree root is the repository root. Checked: ``backend/``, ``scripts/``, ``tests/scripts`` and
        ``tests/swarm_*``. A folder named ``cli`` or ``commands``, or a module with one of these names, is reported
        once. An import of ``argparse``, ``click`` or ``typer`` (``import x``, ``import x.y``, ``from x import y``),
        an attribute ``sys.argv`` and ``from sys import argv`` are reported by line. The harness and the CI scripts
        keep their command lines, because they sit outside these folders.
    """

    NAME: ClassVar[str] = "no_command_line"
    ROOTS: ClassVar[Tuple[str, ...]] = ("backend", "scripts")
    TEST_ROOT: ClassVar[str] = "tests"
    TEST_MIRRORS: ClassVar[Tuple[str, ...]] = ("swarm_", "scripts")
    SKIPPED: ClassVar[Tuple[str, ...]] = ("__pycache__", "node_modules", ".venv")
    PARSERS: ClassVar[Set[str]] = {"argparse", "click", "typer"}
    FORBIDDEN_NAMES: ClassVar[Set[str]] = {"cli"}
    API_ONLY_NAMES: ClassVar[Set[str]] = {"commands"}
    API_HOMES: ClassVar[Set[str]] = {"swarm_api", "api", "apps"}
    SYS: ClassVar[str] = "sys"
    ARGV: ClassVar[str] = "argv"

    ############################
    # Internal Helpers Methods #
    ############################

    def _checked_roots(self, service: ServiceTree) -> List[Path]:
        """List the folders the rule reads.

        Args:
            service (ServiceTree): The tree whose root is the repository root.

        Returns:
            List[Path]: The existing folders among ``backend``, ``scripts``, ``tests/scripts`` and ``tests/swarm_*``.
        """
        roots = [service.root / name for name in self.ROOTS]
        tests = service.root / self.TEST_ROOT
        if tests.is_dir():
            roots.extend(
                child
                for child in sorted(tests.iterdir())
                if child.name.startswith(self.TEST_MIRRORS[0]) or child.name == self.TEST_MIRRORS[1]
            )
        return [root for root in roots if root.is_dir()]

    def _entries(self, root: Path) -> Tuple[List[Path], List[Path]]:
        """Walk a folder.

        Args:
            root (Path): The folder to walk.

        Returns:
            Tuple[List[Path], List[Path]]: The folders (the root included) and the Python files, sorted.
        """
        folders: List[Path] = [root]
        files: List[Path] = []
        for folder, names, filenames in os.walk(root):
            names[:] = sorted(name for name in names if name not in self.SKIPPED)
            folders.extend(Path(folder) / name for name in names)
            files.extend(Path(folder) / name for name in filenames if name.endswith(".py"))
        return folders, sorted(files)

    def _command_line_in_api(self, path: Path) -> bool:
        """Tell whether a folder or module named ``commands`` sits in an api layer or an app.

        Args:
            path (Path): The folder or the module.

        Returns:
            bool: True when its name means a command line there. Elsewhere, ``commands`` is the Drone Command domain.
        """
        return path.stem in self.API_ONLY_NAMES and any(part in self.API_HOMES for part in path.parts[:-1])

    def _import_problems(self, tree: ast.Module) -> List[Tuple[int, str]]:
        """Find the command line imports and ``sys.argv`` uses of a module.

        Args:
            tree (ast.Module): The module.

        Returns:
            List[Tuple[int, str]]: The line and the message of each use.
        """
        found: List[Tuple[int, str]] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                found.extend(
                    (node.lineno, f"Import of {alias.name!r} builds a command line.")
                    for alias in node.names
                    if alias.name.split(".")[0] in self.PARSERS
                )
            elif isinstance(node, ast.ImportFrom) and node.module:
                top = node.module.split(".")[0]
                if top in self.PARSERS:
                    found.append((node.lineno, f"Import from {node.module!r} builds a command line."))
                elif top == self.SYS and any(alias.name == self.ARGV for alias in node.names):
                    found.append((node.lineno, "Import of 'sys.argv' reads a command line."))
            elif (
                isinstance(node, ast.Attribute)
                and node.attr == self.ARGV
                and isinstance(node.value, ast.Name)
                and node.value.id == self.SYS
            ):
                found.append((node.lineno, "Use of 'sys.argv' reads a command line."))
        return found

    ############################
    # Publicly Exposed Methods #
    ############################

    def violations(self, service: ServiceTree) -> List[str]:
        """List the command line code of ``backend/``, ``scripts/`` and their test mirrors.

        Args:
            service (ServiceTree): The tree whose root is the repository root.

        Returns:
            List[str]: One message per refused name, import or use, empty when none of the folders exists.
        """
        messages: List[str] = []
        for root in self._checked_roots(service):
            folders, files = self._entries(root)
            for folder in folders:
                if folder.name in self.FORBIDDEN_NAMES or self._command_line_in_api(folder):
                    messages.append(self.violation(service, folder, None, f"Folder {folder.name!r} is a command line."))
            for path in files:
                if path.stem in self.FORBIDDEN_NAMES or self._command_line_in_api(path):
                    messages.append(self.violation(service, path, None, f"Module {path.stem!r} is a command line."))
                for line, message in self._import_problems(self.parse(path)):
                    messages.append(self.violation(service, path, line, message))
        return messages
