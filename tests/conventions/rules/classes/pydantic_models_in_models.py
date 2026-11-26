from __future__ import annotations

# Standard library imports
import ast
from pathlib import Path
from typing import ClassVar, Dict, List, Set, Tuple

# First-party imports
from tests.conventions.rules.convention_rule import ConventionRule
from tests.conventions.rules.service_tree import ServiceTree


class PydanticModelsInModels(ConventionRule):
    """Pydantic models live in ``src/models/`` and nowhere else.

    Attributes:
        NAME (str): The short name of the rule.
        BASES (Tuple[str, ...]): The base class names that make a class a Pydantic model.

    Notes:
        - A class is a model when a base resolves to ``BASES``, directly or through classes of the same service.
        - **Tests are checked too**, so a model never hides in a test file.
    """

    NAME: ClassVar[str] = "pydantic_models_in_models"
    MODELS_PACKAGE: ClassVar[str] = "swarm-models"
    BASES: ClassVar[Tuple[str, ...]] = ("BaseModel", "RootModel")

    ############################
    # Internal Helpers Methods #
    ############################

    def _base_name(self, node: ast.expr) -> str:
        """Read the name of a base class expression.

        Args:
            node (ast.expr): The base expression.

        Returns:
            str: The name, the attribute, or the name under a subscript. Empty when it cannot be read.
        """
        if isinstance(node, ast.Subscript):
            return self._base_name(node.value)
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            return node.attr
        return ""

    def _is_model(self, name: str, classes: Dict[str, Set[str]], seen: Set[str]) -> bool:
        """Tell whether a class resolves to a Pydantic base.

        Args:
            name (str): The class name.
            classes (Dict[str, Set[str]]): Base names by class name.
            seen (Set[str]): The names already visited, which guards against cycles.

        Returns:
            bool: True when a base is in ``BASES`` or is itself a model.
        """
        if name in seen:
            return False
        seen.add(name)
        for base in classes.get(name, set()):
            if base in self.BASES or self._is_model(base, classes, seen):
                return True
        return False

    ############################
    # Publicly Exposed Methods #
    ############################

    def violations(self, service: ServiceTree) -> List[str]:
        """List the models defined outside the models layer.

        Args:
            service (ServiceTree): The service to check.

        Returns:
            List[str]: One message per model class outside ``src/models/``.
        """
        if service.name == self.MODELS_PACKAGE:
            return []
        trees: Dict[Path, ast.Module] = {path: self.parse(path) for path in service.python_files()}
        classes: Dict[str, Set[str]] = {}
        for tree in trees.values():
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    bases = {self._base_name(base) for base in node.bases}
                    classes.setdefault(node.name, set()).update(bases)
        found: List[str] = []
        for path, tree in trees.items():
            if service.layer_of(path) == "models":
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and self._is_model(node.name, classes, set()):
                    found.append(
                        self.violation(service, path, node.lineno, f"{node.name} is a Pydantic model outside models.")
                    )
        return found
