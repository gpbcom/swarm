from __future__ import annotations

# Standard library imports
from typing import List

# First-party imports
from tests.conventions.rules.classes.lifecycle_base_classes import LifecycleBaseClasses
from tests.conventions.rules.classes.pydantic_models_in_models import PydanticModelsInModels
from tests.conventions.rules.code.no_any import NoAny
from tests.conventions.rules.code.no_nested_function import NoNestedFunction
from tests.conventions.rules.convention_rule import ConventionRule
from tests.conventions.rules.docstrings.no_module_docstring import NoModuleDocstring
from tests.conventions.rules.files.five_files_per_folder import FiveFilesPerFolder
from tests.conventions.rules.files.one_class_per_file import OneClassPerFile
from tests.conventions.rules.imports.import_sections import ImportSections
from tests.conventions.rules.layers.layer_imports import LayerImports
from tests.conventions.rules.logging.no_logger_argument import NoLoggerArgument


class ConventionRules:
    """The registry of every rule that the convention tests run on every Python package and on the tests.

    Notes:
        - **Adding a rule means adding it to ``all`` here.** Nothing else changes.
        - Adding a package needs no change: the tests run every rule on every package ``PackageTree.discover``
          finds in ``backend/`` and ``scripts/``, and on the central ``tests/``.
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
            NoModuleDocstring(),
            NoLoggerArgument(),
            ImportSections(),
        ]
