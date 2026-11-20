from __future__ import annotations

# Standard library imports
from typing import List

# First-party imports
from tests.conventions.rules.classes.lifecycle_base_classes import LifecycleBaseClasses
from tests.conventions.rules.classes.pydantic_models_in_models import PydanticModelsInModels
from tests.conventions.rules.code.no_any import NoAny
from tests.conventions.rules.code.no_nested_function import NoNestedFunction
from tests.conventions.rules.convention_rule import ConventionRule
from tests.conventions.rules.files.five_files_per_folder import FiveFilesPerFolder
from tests.conventions.rules.files.one_class_per_file import OneClassPerFile
from tests.conventions.rules.layers.layer_imports import LayerImports


class ConventionRules:
    """The registry of every rule that the convention tests run on every service.

    Notes:
        - **Adding a rule means adding it to ``all`` here.** Nothing else changes.
        - Adding a service needs no change: the tests run every rule on every folder of ``services/``.
    """

    ############################
    # Publicly Exposed Methods #
    ############################

    @classmethod
    def all(cls) -> List[ConventionRule]:
        """Build one new instance of each rule.

        Returns:
            List[ConventionRule]: The rules, in the order the tests run them.
        """
        return [
            OneClassPerFile(),
            FiveFilesPerFolder(),
            NoAny(),
            NoNestedFunction(),
            LayerImports(),
            LifecycleBaseClasses(),
            PydanticModelsInModels(),
        ]
