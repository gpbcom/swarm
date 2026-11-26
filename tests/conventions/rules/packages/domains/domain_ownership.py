from __future__ import annotations

# Standard library imports
from pathlib import Path
from typing import ClassVar, Dict, List, Set, Tuple

# First-party imports
from tests.conventions.rules.trees.backend_rule import BackendRule
from tests.conventions.rules.trees.imported_names import ImportedNames
from tests.conventions.rules.trees.package_tree import PackageTree


class DomainOwnership(BackendRule):
    """Rule: a domain is used by its own code only, and is owned by exactly one app.

    Attributes:
        NAME (str): The short name of the rule.
        SHARED (str): The folder every domain may use in a layer.
        API_VERSION (str): The folder of the versioned routers in ``swarm_api``.
        API_SHARED (Tuple[str, ...]): The folders of ``swarm_api.v1`` that belong to no domain.
        SERVICE (str): The module of the service layer.
        API (str): The module of the api layer.
        DOMAIN_LAYERS (Tuple[str, ...]): The modules whose first folder is a domain.

    Notes:
        - ``swarm_service.<d>`` uses only ``swarm_storage.<d>``, ``swarm_clients.<d>`` or ``shared``.
        - A domain is a folder of ``swarm_service``, ``swarm_storage`` or ``swarm_clients`` other than ``shared``.
        - An app wires only the domains it lists in ``[tool.swarm] domains``.
    """

    NAME: ClassVar[str] = "domain_ownership"
    SHARED: ClassVar[str] = "shared"
    API_VERSION: ClassVar[str] = "v1"
    API_SHARED: ClassVar[Tuple[str, ...]] = ("live",)
    SERVICE: ClassVar[str] = "swarm_service"
    API: ClassVar[str] = "swarm_api"
    DOMAIN_LAYERS: ClassVar[Tuple[str, ...]] = ("swarm_storage", "swarm_clients")

    ############################
    # Internal Helpers Methods #
    ############################

    def _domain_of(self, name: str) -> str:
        """Read the domain an imported name points to.

        Args:
            name (str): The dotted name.

        Returns:
            str: The domain, or an empty string when the name points to no domain.
        """
        parts = name.split(".")
        if parts[0] in (self.SERVICE, *self.DOMAIN_LAYERS) and len(parts) > 1:
            return parts[1]
        if parts[0] == self.API and len(parts) > 2 and parts[1] == self.API_VERSION:
            return parts[2]
        return ""

    def _service_violations(self, root: Path, package: PackageTree) -> List[str]:
        """List the imports of a domain's service code that reach another domain.

        Args:
            root (Path): The repository root.
            package (PackageTree): The service package.

        Returns:
            List[str]: One message per import of another domain's storage or clients.
        """
        found: List[str] = []
        for path in package.python_files():
            parts = path.relative_to(package.module_dir).parts
            if len(parts) < 2 or parts[0] == self.SHARED:
                continue
            for line, name in ImportedNames.of(self.parse(path)):
                domain = self._domain_of(name)
                if name.split(".")[0] in self.DOMAIN_LAYERS and domain not in (parts[0], self.SHARED):
                    message = f"The {parts[0]} domain must not import {name}."
                    found.append(self.violation(root, path, line, message))
        return found

    def _app_violations(self, root: Path, app: PackageTree) -> List[str]:
        """List the imports of an app that wire a domain it does not list.

        Args:
            root (Path): The repository root.
            app (PackageTree): The app.

        Returns:
            List[str]: One message per import of an unlisted domain.
        """
        listed = set(app.domains()) | {self.SHARED, *self.API_SHARED}
        found: List[str] = []
        for path in app.python_files():
            for line, name in ImportedNames.of(self.parse(path)):
                domain = self._domain_of(name)
                if domain and domain not in listed:
                    message = f"The app {app.name} wires {name}, but does not list the domain {domain}."
                    found.append(self.violation(root, path, line, message))
        return found

    def _existing_domains(self, packages: List[PackageTree]) -> Set[str]:
        """List the domains found as folders of the service, storage and clients packages.

        Args:
            packages (List[PackageTree]): Every package of the repository.

        Returns:
            Set[str]: The folder names, without ``shared`` and private folders.
        """
        domains: Set[str] = set()
        for package in packages:
            if package.module not in (self.SERVICE, *self.DOMAIN_LAYERS) or not package.module_dir.is_dir():
                continue
            for folder in package.module_dir.iterdir():
                if folder.is_dir() and folder.name != self.SHARED and not folder.name.startswith(("_", ".")):
                    domains.add(folder.name)
        return domains

    ############################
    # Publicly Exposed Methods #
    ############################

    def violations(self, root: Path) -> List[str]:
        """List the domain ownership violations of a repository.

        Args:
            root (Path): The repository root.

        Returns:
            List[str]: One message per cross-domain import, unlisted wiring, unowned or shared domain.
        """
        packages = PackageTree.discover(root)
        found: List[str] = []
        owners: Dict[str, List[str]] = {}
        for package in packages:
            if package.module == self.SERVICE:
                found.extend(self._service_violations(root, package))
            elif package.role == PackageTree.APP:
                found.extend(self._app_violations(root, package))
                for domain in package.domains():
                    owners.setdefault(domain, []).append(package.name)
        for domain in sorted(self._existing_domains(packages) | set(owners)):
            apps = owners.get(domain, [])
            if len(apps) != 1:
                message = f"The domain {domain} must be listed by exactly one app, not {len(apps)}: {sorted(apps)}."
                found.append(f"{PackageTree.BACKEND_FOLDER}/{PackageTree.APPS_FOLDER}: {message}")
        return found
