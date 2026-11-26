from __future__ import annotations

# Standard library imports
import re
import tomllib
from pathlib import Path
from typing import ClassVar, List, Set

# First-party imports
from tests.conventions.rules.trees.backend_rule import BackendRule
from tests.conventions.rules.trees.imported_names import ImportedNames
from tests.conventions.rules.trees.package_tree import PackageTree


class PackageDependencies(BackendRule):
    """Rule: a layer package declares exactly the first-party packages its imports need.

    Attributes:
        NAME (str): The short name of the rule.
        REQUIREMENT_NAME (re.Pattern[str]): Reads the distribution name at the start of a requirement.

    Notes:
        - The declared packages are the ``dependencies`` and every ``optional-dependencies`` extra of the project
          file, so that per-domain extras count.
        - Only the layer packages are checked, and only the first-party names (packages found in the repository).
    """

    NAME: ClassVar[str] = "package_dependencies"
    REQUIREMENT_NAME: ClassVar[re.Pattern[str]] = re.compile(r"^\s*([A-Za-z0-9][A-Za-z0-9._-]*)")

    ############################
    # Internal Helpers Methods #
    ############################

    def _declared(self, package: PackageTree) -> Set[str]:
        """Read the module names of the dependencies a package declares.

        Args:
            package (PackageTree): The package whose project file is read.

        Returns:
            Set[str]: The distribution names with ``-`` written ``_``.
        """
        data = tomllib.loads(package.pyproject.read_text(encoding=PackageTree.ENCODING))
        project = data.get("project", {})
        requirements: List[str] = list(project.get("dependencies", []))
        for extra in project.get("optional-dependencies", {}).values():
            requirements.extend(extra)
        names: Set[str] = set()
        for requirement in requirements:
            match = self.REQUIREMENT_NAME.match(requirement)
            if match:
                names.add(match.group(1).replace("-", "_").lower())
        return names

    def _needed(self, package: PackageTree, known: Set[str]) -> Set[str]:
        """List the first-party modules a package imports.

        Args:
            package (PackageTree): The importing package.
            known (Set[str]): The module names of every package of the repository.

        Returns:
            Set[str]: The imported first-party modules, the package itself left out.
        """
        needed: Set[str] = set()
        for path in package.python_files():
            for _, name in ImportedNames.of(self.parse(path)):
                top = name.split(".")[0]
                if top in known and top != package.module:
                    needed.add(top)
        return needed

    ############################
    # Publicly Exposed Methods #
    ############################

    def violations(self, root: Path) -> List[str]:
        """List the missing and the unused first-party dependencies of each layer package.

        Args:
            root (Path): The repository root.

        Returns:
            List[str]: One message per missing or unused dependency.
        """
        packages = PackageTree.discover(root)
        known = {package.module for package in packages}
        found: List[str] = []
        for package in packages:
            if package.role not in PackageTree.LAYERS:
                continue
            if not package.pyproject.is_file():
                found.append(self.violation(root, package.folder, None, "The package has no pyproject.toml."))
                continue
            declared = self._declared(package) & known
            needed = self._needed(package, known)
            for module in sorted(needed - declared):
                message = f"The imports need {module}, which the project file does not declare."
                found.append(self.violation(root, package.pyproject, None, message))
            for module in sorted(declared - needed - {package.module}):
                message = f"The project file declares {module}, which no import needs."
                found.append(self.violation(root, package.pyproject, None, message))
        return found
