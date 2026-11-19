from __future__ import annotations

# Standard library imports
from pathlib import Path
from typing import ClassVar, List, Optional, Tuple


class ServiceTree:
    """One service folder of the mono-repo, as the convention rules walk it.

    Attributes:
        LAYERS (Tuple[str, ...]): The five layers a service source package holds.
        root (Path): The service folder, such as ``services/gateway``.

    Notes:
        A new service is found by ``discover`` without any change to the convention tests.
    """

    LAYERS: ClassVar[Tuple[str, ...]] = ("api", "service", "storage", "clients", "models")

    def __init__(self, root: Path) -> None:
        """Initialise the tree.

        Args:
            root (Path): The service folder.
        """
        self.root = root

    ############################
    # Internal Helpers Methods #
    ############################

    def _is_skipped(self, path: Path) -> bool:
        """Tell whether a file sits in a ``__pycache__`` or hidden folder.

        Args:
            path (Path): The file to test.

        Returns:
            bool: True when the file must be ignored.
        """
        parts = path.relative_to(self.root).parts[:-1]
        return any(part == "__pycache__" or part.startswith(".") for part in parts)

    def _source_parts(self, path: Path) -> Optional[Tuple[str, ...]]:
        """Return the parts of a path under ``src/``.

        Args:
            path (Path): The path to split.

        Returns:
            Optional[Tuple[str, ...]]: The parts after ``src/``, or None when the path is not under it.
        """
        try:
            return path.relative_to(self.source_root).parts
        except ValueError:
            return None

    ############################
    # Publicly Exposed Methods #
    ############################

    @classmethod
    def discover(cls, services_root: Path) -> List[ServiceTree]:
        """Find every service under a folder.

        Args:
            services_root (Path): The folder holding the services.

        Returns:
            List[ServiceTree]: One tree per sub-folder not starting with ``.`` or ``_``, sorted by name.
                Empty when the folder is missing.
        """
        if not services_root.is_dir():
            return []
        folders = [
            child for child in services_root.iterdir() if child.is_dir() and not child.name.startswith((".", "_"))
        ]
        return [cls(folder) for folder in sorted(folders, key=lambda folder: folder.name)]

    @property
    def name(self) -> str:
        """The service name, which is its folder name."""
        return self.root.name

    @property
    def source_root(self) -> Path:
        """The ``src`` folder of the service."""
        return self.root / "src"

    @property
    def tests_root(self) -> Path:
        """The ``tests`` folder of the service."""
        return self.root / "tests"

    def python_files(self) -> List[Path]:
        """List the Python files of the service.

        Returns:
            List[Path]: Every ``*.py`` file under ``src/`` and ``tests/``, sorted, without ``__pycache__`` and
                hidden folders.
        """
        files: List[Path] = []
        for folder in (self.source_root, self.tests_root):
            if folder.is_dir():
                files.extend(path for path in folder.rglob("*.py") if not self._is_skipped(path))
        return sorted(files)

    def package_of(self, path: Path) -> Optional[str]:
        """Return the source package a file belongs to.

        Args:
            path (Path): The file to place.

        Returns:
            Optional[str]: The folder right under ``src/``, or None when the file is not in a package there.
        """
        parts = self._source_parts(path)
        if parts is None or len(parts) < 2:
            return None
        return parts[0]

    def layer_of(self, path: Path) -> Optional[str]:
        """Return the layer a file belongs to.

        Args:
            path (Path): The file to place.

        Returns:
            Optional[str]: The folder right under ``src/<package>/`` when it is in ``LAYERS``, else None.
        """
        parts = self._source_parts(path)
        if parts is None or len(parts) < 3:
            return None
        return parts[1] if parts[1] in self.LAYERS else None

    def relative(self, path: Path) -> str:
        """Return a path relative to the service folder.

        Args:
            path (Path): The path to convert.

        Returns:
            str: The POSIX path from the service root.
        """
        return path.relative_to(self.root).as_posix()
