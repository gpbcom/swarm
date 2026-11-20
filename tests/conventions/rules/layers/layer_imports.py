from __future__ import annotations

# Standard library imports
import ast
from typing import ClassVar, Dict, List, Optional, Set, Tuple, Union

# First-party imports
from tests.conventions.rules.convention_rule import ConventionRule
from tests.conventions.rules.service_tree import ServiceTree


class LayerImports(ConventionRule):
    """Rule: a layer only imports the layers AGENT.md allows it.

    Attributes:
        NAME (str): The short name of the rule.
        ALLOWED (Dict[str, Tuple[str, ...]]): For each layer, the layers it may import, itself included.

    Notes:
        - Every import in the tree is checked, ``TYPE_CHECKING`` blocks included.
        - Files in ``tests/`` and directly in ``src/<package>/`` are not checked.
    """

    NAME: ClassVar[str] = "layer_imports"
    ALLOWED: ClassVar[Dict[str, Tuple[str, ...]]] = {
        "api": ("api", "service", "models"),
        "service": ("service", "storage", "clients", "models"),
        "storage": ("storage", "models"),
        "clients": ("clients", "models"),
        "models": ("models",),
    }

    ############################
    # Internal Helpers Methods #
    ############################

    def _absolute_names(self, node: Union[ast.Import, ast.ImportFrom], file_package: List[str]) -> List[List[str]]:
        """Resolve the dotted names an import statement refers to.

        Args:
            node (Union[ast.Import, ast.ImportFrom]): The import statement.
            file_package (List[str]): The dotted package of the file, as parts.

        Returns:
            List[List[str]]: One list of name parts per target. A ``from`` import of a bare package yields one per
                imported name.
        """
        if isinstance(node, ast.Import):
            return [alias.name.split(".") for alias in node.names]
        base: List[str] = []
        if node.level > 0:
            base = file_package[: max(len(file_package) - (node.level - 1), 0)]
        module = base + (node.module.split(".") if node.module else [])
        if len(module) > 1:
            return [module]
        return [module + [alias.name] for alias in node.names]

    def _target_layer(self, parts: List[str], package: str, layers: Tuple[str, ...]) -> Optional[str]:
        """Find the layer a dotted name points to.

        Args:
            parts (List[str]): The dotted name, split.
            package (str): The source package of the service.
            layers (Tuple[str, ...]): The known layers.

        Returns:
            Optional[str]: The layer, or None for an import outside the layers.
        """
        if parts and parts[0] == package:
            parts = parts[1:]
        elif not parts or parts[0] not in layers:
            return None
        if parts and parts[0] in layers:
            return parts[0]
        return None

    def _refused_targets(
        self, node: Union[ast.Import, ast.ImportFrom], file_package: List[str], package: str, source: str
    ) -> Set[str]:
        """List the layers an import statement targets that its layer may not import.

        Args:
            node (Union[ast.Import, ast.ImportFrom]): The import statement.
            file_package (List[str]): The dotted package of the file, as parts.
            package (str): The source package of the service.
            source (str): The layer of the importing file.

        Returns:
            Set[str]: The refused target layers, empty when the import is allowed.
        """
        refused: Set[str] = set()
        for parts in self._absolute_names(node, file_package):
            target = self._target_layer(parts, package, ServiceTree.LAYERS)
            if target is not None and target not in self.ALLOWED[source]:
                refused.add(target)
        return refused

    ############################
    # Publicly Exposed Methods #
    ############################

    def violations(self, service: ServiceTree) -> List[str]:
        """List the imports that cross a forbidden layer boundary.

        Args:
            service (ServiceTree): The service to check.

        Returns:
            List[str]: One message per import statement with a refused target.
        """
        found: List[str] = []
        for path in service.python_files():
            source = service.layer_of(path)
            package = service.package_of(path)
            if source is None or package is None:
                continue
            file_package = list(path.relative_to(service.source_root).parts[:-1])
            for node in ast.walk(self.parse(path)):
                if not isinstance(node, (ast.Import, ast.ImportFrom)):
                    continue
                refused = sorted(self._refused_targets(node, file_package, package, source))
                if refused:
                    message = f"The {source} layer must not import the {', '.join(refused)} layer."
                    found.append(self.violation(service, path, node.lineno, message))
        return found
