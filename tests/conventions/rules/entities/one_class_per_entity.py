from __future__ import annotations

# Standard library imports
import ast
import os
from pathlib import Path
from typing import ClassVar, Dict, List, Set, Tuple

# First-party imports
from tests.conventions.rules.convention_rule import ConventionRule
from tests.conventions.rules.service_tree import ServiceTree


class OneClassPerEntity(ConventionRule):
    """Within a layer package, an entity has one class: one repository, one client, one service, one router.

    Attributes:
        NAME (str): The short name of the rule.
        BACKEND (str): The folder, under the tree root, searched for layer packages.
        ROLES (Dict[str, str]): The fixed class name ending of each layer package.
        SKIPPED (Tuple[str, ...]): The folders never entered.
        FACTORY_SUFFIX (str): The class name ending of a factory, which is exempt.
        EXCEPTION_PREFIX (str): The class name start of an exception, which is exempt.

    Notes:
        The tree root is the repository root. Every folder named ``swarm_storage``, ``swarm_clients``,
        ``swarm_service`` or ``swarm_api`` under ``backend/`` is one layer, whatever the folder it sits in.
        - A top-level class is read as ``<Entity><Role>``, the role being the layer's: ``Repository``, ``Client``,
          ``Service`` or ``Router``. A class with another ending is ignored, and so is one that is only the role.
        - ``*Factory`` classes and ``SE*`` exceptions are exempt.
        - Two classes with the same entity in one layer are one violation, naming both classes and both files.
          The meaning of an entity is left to the reviewer.
    """

    NAME: ClassVar[str] = "one_class_per_entity"
    BACKEND: ClassVar[str] = "backend"
    ROLES: ClassVar[Dict[str, str]] = {
        "swarm_storage": "Repository",
        "swarm_clients": "Client",
        "swarm_service": "Service",
        "swarm_api": "Router",
    }
    SKIPPED: ClassVar[Tuple[str, ...]] = ("__pycache__", "node_modules")
    FACTORY_SUFFIX: ClassVar[str] = "Factory"
    EXCEPTION_PREFIX: ClassVar[str] = "SE"

    ############################
    # Internal Helpers Methods #
    ############################

    def _layers(self, service: ServiceTree) -> List[Path]:
        """Find the layer packages under ``backend/``.

        Args:
            service (ServiceTree): The tree whose root is the repository root.

        Returns:
            List[Path]: The sorted folders named like a layer package.
        """
        layers: List[Path] = []
        for folder, names, _ in os.walk(service.root / self.BACKEND):
            names[:] = [name for name in names if name not in self.SKIPPED]
            layers.extend(Path(folder) / name for name in names if name in self.ROLES)
        return sorted(layers)

    def _entity(self, name: str, role: str) -> str:
        """Read the entity of a class name.

        Args:
            name (str): The class name.
            role (str): The role of the layer.

        Returns:
            str: The name without its role, or an empty string when the class is exempt or has no entity.
        """
        if name.endswith(self.FACTORY_SUFFIX) or name.startswith(self.EXCEPTION_PREFIX):
            return ""
        if not name.endswith(role):
            return ""
        return name[: -len(role)]

    ############################
    # Publicly Exposed Methods #
    ############################

    def violations(self, service: ServiceTree) -> List[str]:
        """List the entities that have several classes in one layer.

        Args:
            service (ServiceTree): The tree whose root is the repository root.

        Returns:
            List[str]: One message per entity and layer, empty when there is no ``backend/``.
        """
        messages: List[str] = []
        for layer in self._layers(service):
            role = self.ROLES[layer.name]
            found: Dict[str, List[Tuple[str, Path, int]]] = {}
            for path in sorted(layer.rglob("*.py")):
                if self.SKIPPED[0] in path.parts:
                    continue
                for node in self.parse(path).body:
                    if isinstance(node, ast.ClassDef) and self._entity(node.name, role):
                        found.setdefault(self._entity(node.name, role), []).append((node.name, path, node.lineno))
            for entity, classes in sorted(found.items()):
                if len(classes) < 2:
                    continue
                names = ", ".join(sorted(name for name, _, _ in classes))
                files: Set[str] = {service.relative(path) for _, path, _ in classes}
                _, path, line = classes[1]
                messages.append(
                    self.violation(
                        service,
                        path,
                        line,
                        f"Entity {entity!r} has several {role} classes in {layer.name}: {names}. "
                        f"Merge them into {entity}{role} ({', '.join(sorted(files))}).",
                    )
                )
        return messages
