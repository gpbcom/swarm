from __future__ import annotations

# Standard library imports
from pathlib import Path
from typing import ClassVar, Dict, List, Set, Tuple

# First-party imports
from tests.conventions.rules.trees.backend_rule import BackendRule
from tests.conventions.rules.trees.imported_names import ImportedNames
from tests.conventions.rules.trees.package_tree import PackageTree


class PackageImports(BackendRule):
    """Rule: a package only imports the first-party packages AGENT.md allows it.

    Attributes:
        NAME (str): The short name of the rule.
        SELF (str): The token for the package itself in ``ALLOWED``.
        KERNEL (str): The token for every kernel lib in ``ALLOWED``.
        APP (str): The token for the app name in ``ALLOWED``.
        ALLOWED (Dict[str, Tuple[str, ...]]): For each role, the dotted prefixes its code may import.

    Notes:
        - Only imports of a package found in the repository are checked: a third-party import is never refused.
        - Every import is checked, ``TYPE_CHECKING`` blocks included.
        - ``swarm_models`` may import the models of the kernel's ``swarm_web`` and ``swarm_nats`` (``RestConfig``,
          ``NatsClientConfig``), which the apps' configurations embed, and nothing else of them.
    """

    NAME: ClassVar[str] = "package_imports"
    SELF: ClassVar[str] = "{self}"
    KERNEL: ClassVar[str] = "{kernel}"
    APP: ClassVar[str] = "{app}"
    ALLOWED: ClassVar[Dict[str, Tuple[str, ...]]] = {
        "kernel": ("{kernel}",),
        "models": ("{self}", "swarm_catalog", "swarm_lifecycle", "swarm_web.models", "swarm_nats.models"),
        "storage": ("{self}", "swarm_models", "{kernel}"),
        "clients": ("{self}", "swarm_models", "{kernel}"),
        "service": ("{self}", "swarm_storage", "swarm_clients", "swarm_models", "{kernel}"),
        "api": ("{self}", "swarm_service", "swarm_models", "{kernel}"),
        "app": ("{self}", "swarm_api", "swarm_service", "swarm_web", "swarm_models.config.{app}", "swarm_logging"),
        "scripts": ("swarm_service", "swarm_api", "swarm_web", "swarm_models", "{kernel}"),
    }

    ############################
    # Internal Helpers Methods #
    ############################

    def _allowed(self, package: PackageTree, kernel: List[str]) -> Set[str]:
        """Expand the allowed prefixes of a package.

        Args:
            package (PackageTree): The importing package.
            kernel (List[str]): The module names of the kernel libs.

        Returns:
            Set[str]: The dotted prefixes the package may import.
        """
        allowed: Set[str] = set()
        for entry in self.ALLOWED[package.role]:
            if entry == self.KERNEL:
                allowed.update(kernel)
            else:
                allowed.add(entry.replace(self.SELF, package.module).replace(self.APP, package.app_name))
        return allowed

    ############################
    # Publicly Exposed Methods #
    ############################

    def violations(self, root: Path) -> List[str]:
        """List the imports that cross a forbidden package boundary.

        Args:
            root (Path): The repository root.

        Returns:
            List[str]: One message per refused imported name.
        """
        packages = PackageTree.discover(root)
        known = {package.module for package in packages}
        kernel = [package.module for package in packages if package.role == PackageTree.KERNEL]
        found: List[str] = []
        for package in packages:
            allowed = self._allowed(package, kernel)
            for path in package.python_files():
                for line, name in ImportedNames.of(self.parse(path)):
                    if name.split(".")[0] not in known:
                        continue
                    if any(name == prefix or name.startswith(prefix + ".") for prefix in allowed):
                        continue
                    message = f"The {package.role} package {package.module} must not import {name}."
                    found.append(self.violation(root, path, line, message))
        return found
