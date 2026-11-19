from __future__ import annotations

# Standard library imports
from pathlib import Path
from typing import ClassVar, Dict, List, Tuple

# First-party imports
from tests.conventions.rules.convention_rule import ConventionRule
from tests.conventions.rules.service_tree import ServiceTree


class FiveFilesPerFolder(ConventionRule):
    """No folder of ``src/`` or ``tests/`` holds more than five Python files.

    Attributes:
        NAME (str): The short name of the rule.
        MAX_FILES (int): The most Python files a folder may hold.
        IGNORED (Tuple[str, ...]): The file names that do not count towards the limit.

    Notes:
        A folder that would go past the limit is split into sub-folders, by entity type.
    """

    NAME: ClassVar[str] = "five_files_per_folder"
    MAX_FILES: ClassVar[int] = 5
    IGNORED: ClassVar[Tuple[str, ...]] = ("__init__.py", "conftest.py")

    ############################
    # Publicly Exposed Methods #
    ############################

    def violations(self, service: ServiceTree) -> List[str]:
        """List the folders that hold too many Python files.

        Args:
            service (ServiceTree): The service to check.

        Returns:
            List[str]: One message per crowded folder, empty when the service complies.
        """
        counts: Dict[Path, int] = {}
        for path in service.python_files():
            if path.name not in self.IGNORED:
                counts[path.parent] = counts.get(path.parent, 0) + 1
        return [
            self.violation(
                service,
                folder,
                None,
                f"The folder holds {count} Python files. The most allowed is {self.MAX_FILES}.",
            )
            for folder, count in sorted(counts.items())
            if count > self.MAX_FILES
        ]
