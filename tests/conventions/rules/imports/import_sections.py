from __future__ import annotations

# Standard library imports
import ast
import sys
import tomllib
from pathlib import Path
from typing import ClassVar, Dict, List, Optional, Set, Tuple

# First-party imports
from tests.conventions.rules.convention_rule import ConventionRule
from tests.conventions.rules.service_tree import ServiceTree


class ImportSections(ConventionRule):
    """Every import of a module sits under the comment of its section, and the sections come in order.

    Attributes:
        NAME (str): The short name of the rule.
        STANDARD (str): The key and order of the standard library section.
        THIRD_PARTY (str): The key and order of the third-party section.
        FIRST_PARTY (str): The key and order of the first-party section.
        ORDER (Tuple[str, ...]): The sections in the order a module lists them.
        HEADERS (Dict[str, str]): The comment above each section.
        NAMESPACES (Tuple[str, ...]): The top folders of the repository that code imports as first-party namespaces.
        INIT (str): The file name the rule skips: an ``__init__.py`` only re-exports.
        FUTURE (str): The ``__future__`` module, which comes before every section.

    Notes:
        - The imports checked are the ones at the top of the module, after ``from __future__ import annotations``.
        - A module is first-party when it is a package of the service, a namespace of the repository or named in the
          ``known-first-party`` of the nearest ``pyproject.toml`` (above the code, and above this rule, for a service
          checked outside the repository), so that ruff's isort and this rule agree. Where they
          cannot agree, the import stays in its AGENT.md section with ``# isort: skip``.
        - ``src/`` and ``tests/`` are both checked; ``__init__.py`` files are not.
    """

    NAME: ClassVar[str] = "import_sections"
    STANDARD: ClassVar[str] = "standard"
    THIRD_PARTY: ClassVar[str] = "third_party"
    FIRST_PARTY: ClassVar[str] = "first_party"
    ORDER: ClassVar[Tuple[str, ...]] = (STANDARD, THIRD_PARTY, FIRST_PARTY)
    HEADERS: ClassVar[Dict[str, str]] = {
        STANDARD: "# Standard library imports",
        THIRD_PARTY: "# Third-party imports",
        FIRST_PARTY: "# First-party imports",
    }
    NAMESPACES: ClassVar[Tuple[str, ...]] = ("tests", "services", "packages", "backend")
    INIT: ClassVar[str] = "__init__.py"
    FUTURE: ClassVar[str] = "__future__"

    ############################
    # Internal Helpers Methods #
    ############################

    def _top_imports(self, tree: ast.Module) -> List[ast.stmt]:
        """Return the imports at the top of a module, without ``from __future__``.

        Args:
            tree (ast.Module): The syntax tree.

        Returns:
            List[ast.stmt]: The leading ``import`` and ``from`` statements, stopping at the first other statement.
        """
        found: List[ast.stmt] = []
        for node in tree.body:
            if not isinstance(node, (ast.Import, ast.ImportFrom)):
                break
            if not (isinstance(node, ast.ImportFrom) and node.module == self.FUTURE):
                found.append(node)
        return found

    def _module(self, node: ast.stmt) -> str:
        """Return the module an import names, with its leading dots for a relative import.

        Args:
            node (ast.stmt): An ``import`` or ``from`` statement.

        Returns:
            str: The module, such as ``swarm_models.base`` or ``.sibling``.
        """
        if isinstance(node, ast.ImportFrom):
            return "." * node.level + (node.module or "")
        assert isinstance(node, ast.Import)
        return node.names[0].name

    def _known_first_party(self, start: Path) -> Set[str]:
        """Read ``known-first-party`` from the nearest ``pyproject.toml`` that sets it.

        Args:
            start (Path): The folder to look up from.

        Returns:
            Set[str]: The module names ruff's isort treats as first-party, empty when none is found.
        """
        for folder in [start, *start.parents]:
            pyproject = folder / "pyproject.toml"
            if not pyproject.is_file():
                continue
            settings = tomllib.loads(pyproject.read_text(encoding="utf-8"))
            names = settings.get("tool", {}).get("ruff", {}).get("lint", {}).get("isort", {}).get("known-first-party")
            if isinstance(names, list):
                return {str(name) for name in names}
        return set()

    ############################
    # Publicly Exposed Methods #
    ############################

    def first_party(self, root: Path, own: Set[str]) -> Set[str]:
        """Return every module name that counts as first-party for the code under ``root``.

        Args:
            root (Path): A folder of the repository.
            own (Set[str]): The packages of the code being checked.

        Returns:
            Set[str]: Its own packages, the repository's namespaces and the ``known-first-party`` names.
        """
        repository = self._known_first_party(Path(__file__).resolve().parent)
        return {*own, *self.NAMESPACES, *self._known_first_party(root), *repository}

    def section_of(self, module: str, first_party: Set[str]) -> str:
        """Return the section an imported module belongs to.

        Args:
            module (str): The module, with leading dots for a relative import.
            first_party (Set[str]): The first-party module names.

        Returns:
            str: ``STANDARD``, ``THIRD_PARTY`` or ``FIRST_PARTY``.
        """
        top = module.split(".")[0]
        if module.startswith(".") or top in first_party:
            return self.FIRST_PARTY
        if top in sys.stdlib_module_names:
            return self.STANDARD
        return self.THIRD_PARTY

    def problems(self, path: Path, first_party: Set[str]) -> List[Tuple[int, str]]:
        """List the import-section problems of one module.

        Args:
            path (Path): The Python file.
            first_party (Set[str]): The first-party module names.

        Returns:
            List[Tuple[int, str]]: The line and the message of each problem, empty when the module complies.
        """
        if path.name == self.INIT:
            return []
        lines = path.read_text(encoding="utf-8").splitlines()
        imports = self._top_imports(self.parse(path))
        headers = {
            number: key
            for number, line in enumerate(lines, start=1)
            for key, header in self.HEADERS.items()
            if line.strip() == header
        }
        found: List[Tuple[int, str]] = []
        seen: List[str] = []
        for node in imports:
            above: Optional[int] = max((number for number in headers if number < node.lineno), default=None)
            current = headers[above] if above is not None else None
            expected = self.section_of(self._module(node), first_party)
            if current != expected:
                where = self.HEADERS[current] if current else "no section comment"
                found.append(
                    (node.lineno, f"{self._module(node)} belongs under '{self.HEADERS[expected]}', not {where}.")
                )
            if expected not in seen:
                seen.append(expected)
        if seen != [key for key in self.ORDER if key in seen] and imports:
            found.append((imports[0].lineno, "The import sections are out of order."))
        return found

    def violations(self, service: ServiceTree) -> List[str]:
        """List the import-section problems of a service, in ``src/`` and ``tests/``.

        Args:
            service (ServiceTree): The service to check.

        Returns:
            List[str]: One message per problem.
        """
        own = {folder.name for folder in service.source_root.glob("*") if folder.is_dir()}
        first_party = self.first_party(service.root, own)
        messages: List[str] = []
        for path in service.python_files():
            for line, message in self.problems(path, first_party):
                messages.append(self.violation(service, path, line, message))
        return messages
