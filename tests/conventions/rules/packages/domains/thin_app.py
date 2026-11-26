from __future__ import annotations

# Standard library imports
import ast
from pathlib import Path
from typing import ClassVar, List

# First-party imports
from tests.conventions.rules.trees.backend_rule import BackendRule
from tests.conventions.rules.trees.package_tree import PackageTree


class ThinApp(BackendRule):
    """Rule: an app's module holds only ``main.py``, whose ``main()`` takes no argument.

    Attributes:
        NAME (str): The short name of the rule.
        MAIN_FILE (str): The file an app holds.
        MAIN_FUNCTION (str): The function of that file.
        INIT_FILE (str): The package marker an app may hold.
        CACHE_FOLDER (str): The cache folder that is ignored.

    Notes:
        The app reads ``conf/app.yaml`` and its environment, so it needs no command line.
    """

    NAME: ClassVar[str] = "thin_app"
    MAIN_FILE: ClassVar[str] = "main.py"
    MAIN_FUNCTION: ClassVar[str] = "main"
    INIT_FILE: ClassVar[str] = "__init__.py"
    CACHE_FOLDER: ClassVar[str] = "__pycache__"

    ############################
    # Internal Helpers Methods #
    ############################

    def _main_violations(self, root: Path, path: Path) -> List[str]:
        """Check that ``main.py`` defines a ``main()`` without argument.

        Args:
            root (Path): The repository root.
            path (Path): The ``main.py`` file.

        Returns:
            List[str]: The violations of the file.
        """
        for node in self.parse(path).body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == self.MAIN_FUNCTION:
                arguments = node.args
                every = arguments.posonlyargs + arguments.args + arguments.kwonlyargs
                if every or arguments.vararg or arguments.kwarg:
                    return [self.violation(root, path, node.lineno, "The function main() must take no argument.")]
                return []
        return [self.violation(root, path, None, "The file defines no main() function.")]

    ############################
    # Publicly Exposed Methods #
    ############################

    def violations(self, root: Path) -> List[str]:
        """List the apps that hold more than their ``main.py``.

        Args:
            root (Path): The repository root.

        Returns:
            List[str]: One message per extra file or folder, missing ``main.py`` or main() with arguments.
        """
        found: List[str] = []
        for app in PackageTree.discover(root):
            if app.role != PackageTree.APP:
                continue
            if not app.module_dir.is_dir():
                found.append(self.violation(root, app.folder, None, f"The app has no module {app.module}."))
                continue
            for entry in sorted(app.module_dir.iterdir()):
                if entry.name in (self.MAIN_FILE, self.INIT_FILE, self.CACHE_FOLDER):
                    continue
                found.append(self.violation(root, entry, None, "An app holds only main.py and __init__.py."))
            main = app.module_dir / self.MAIN_FILE
            if main.is_file():
                found.extend(self._main_violations(root, main))
            else:
                found.append(self.violation(root, app.module_dir, None, "The app has no main.py."))
        return found
