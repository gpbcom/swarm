from __future__ import annotations

# Standard library imports
from typing import List

# First-party imports
from tests.conventions.rules.packages.domains.domain_ownership import DomainOwnership
from tests.conventions.rules.packages.domains.thin_app import ThinApp
from tests.conventions.rules.packages.imports.package_dependencies import PackageDependencies
from tests.conventions.rules.packages.imports.package_imports import PackageImports
from tests.conventions.rules.tests_layout.names.unique_test_basenames import UniqueTestBasenames
from tests.conventions.rules.tests_layout.no_file_depth_path import NoFileDepthPath
from tests.conventions.rules.tests_layout.tests_mirror import TestsMirror
from tests.conventions.rules.trees.backend_rule import BackendRule


class BackendRules:
    """The rules that the backend convention tests run on the repository's ``backend/`` and ``scripts/``.

    Notes:
        Adding a rule means adding it to ``all`` here. Adding a package or an app needs no change.
    """

    ############################
    # Publicly Exposed Methods #
    ############################

    @classmethod
    def all(cls) -> List[BackendRule]:
        """Build one new instance of each rule.

        Returns:
            List[BackendRule]: The rules, in the order the tests run them.
        """
        return [
            PackageImports(),
            PackageDependencies(),
            DomainOwnership(),
            ThinApp(),
            TestsMirror(),
            UniqueTestBasenames(),
            NoFileDepthPath(),
        ]
