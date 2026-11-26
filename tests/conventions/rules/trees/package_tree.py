from __future__ import annotations

# Standard library imports
import tomllib
from pathlib import Path
from typing import ClassVar, List, Tuple


class PackageTree:
    """One Python package of the backend layout, as the backend convention rules walk it.

    Attributes:
        KERNEL (str): The role of a kernel lib of ``backend/libs/``.
        APP (str): The role of an app of ``backend/apps/``.
        SCRIPTS (str): The role of the top-level ``scripts/`` folder.
        LAYERS (Tuple[str, ...]): The roles of the layer packages ``backend/swarm-<layer>/``.
        PREFIX (str): The prefix of every module name.
        FOLDER_PREFIX (str): The prefix of a layer package folder.
        TOOL_KEY (str): The ``tool`` table of a project file.
        SWARM_KEY (str): The ``swarm`` table of ``tool``.
        DOMAINS_KEY (str): The key listing an app's domains.
        ENCODING (str): The encoding of the project files.
        BACKEND_FOLDER (str): The backend folder of the repository.
        LIBS_FOLDER (str): The folder of the kernel libs, in the backend folder.
        APPS_FOLDER (str): The folder of the apps, in the backend folder.
        SCRIPTS_FOLDER (str): The folder of the scripts, in the repository root.
        SOURCE_FOLDER (str): The folder holding the module of a package.
        TESTS_FOLDER (str): The central tests folder of the repository.
        PYPROJECT (str): The name of a package's project file.
        root (Path): The repository root.
        folder (Path): The package folder, such as ``backend/swarm-service``.
        role (str): ``KERNEL``, a layer, ``APP`` or ``SCRIPTS``.

    Notes:
        A new package is found by ``discover`` without any change to the convention tests.
    """

    KERNEL: ClassVar[str] = "kernel"
    APP: ClassVar[str] = "app"
    SCRIPTS: ClassVar[str] = "scripts"
    LAYERS: ClassVar[Tuple[str, ...]] = ("models", "storage", "clients", "service", "api")
    PREFIX: ClassVar[str] = "swarm_"
    FOLDER_PREFIX: ClassVar[str] = "swarm-"
    BACKEND_FOLDER: ClassVar[str] = "backend"
    LIBS_FOLDER: ClassVar[str] = "libs"
    APPS_FOLDER: ClassVar[str] = "apps"
    SCRIPTS_FOLDER: ClassVar[str] = "scripts"
    SOURCE_FOLDER: ClassVar[str] = "src"
    TESTS_FOLDER: ClassVar[str] = "tests"
    PYPROJECT: ClassVar[str] = "pyproject.toml"
    TOOL_KEY: ClassVar[str] = "tool"
    SWARM_KEY: ClassVar[str] = "swarm"
    DOMAINS_KEY: ClassVar[str] = "domains"
    ENCODING: ClassVar[str] = "utf-8"

    def __init__(self, root: Path, folder: Path, role: str) -> None:
        """Initialise the tree.

        Args:
            root (Path): The repository root.
            folder (Path): The package folder.
            role (str): ``KERNEL``, a layer, ``APP`` or ``SCRIPTS``.
        """
        self.root = root
        self.folder = folder
        self.role = role

    ############################
    # Internal Helpers Methods #
    ############################

    @classmethod
    def _children(cls, parent: Path) -> List[Path]:
        """List the sub-folders of a folder that are not hidden or private.

        Args:
            parent (Path): The folder to list.

        Returns:
            List[Path]: The sorted sub-folders, empty when the folder is missing.
        """
        if not parent.is_dir():
            return []
        return sorted(child for child in parent.iterdir() if child.is_dir() and not child.name.startswith((".", "_")))

    def _is_skipped(self, path: Path) -> bool:
        """Tell whether a file sits in a ``__pycache__`` or hidden folder.

        Args:
            path (Path): The file to test.

        Returns:
            bool: True when the file must be ignored.
        """
        parts = path.relative_to(self.folder).parts[:-1]
        return any(part == "__pycache__" or part.startswith(".") for part in parts)

    ############################
    # Publicly Exposed Methods #
    ############################

    @classmethod
    def discover(cls, root: Path) -> List[PackageTree]:
        """Find every package of the backend layout under a repository root.

        Args:
            root (Path): The repository root, holding ``backend/`` and ``scripts/``.

        Returns:
            List[PackageTree]: The kernel libs, the layer packages, the apps, then the scripts, each sorted by
                folder name. Empty when the root holds none of them.
        """
        backend = root / cls.BACKEND_FOLDER
        found = [cls(root, folder, cls.KERNEL) for folder in cls._children(backend / cls.LIBS_FOLDER)]
        for folder in cls._children(backend):
            layer = folder.name.removeprefix(cls.FOLDER_PREFIX)
            if folder.name.startswith(cls.FOLDER_PREFIX) and layer in cls.LAYERS:
                found.append(cls(root, folder, layer))
        found.extend(cls(root, folder, cls.APP) for folder in cls._children(backend / cls.APPS_FOLDER))
        scripts = root / cls.SCRIPTS_FOLDER
        if scripts.is_dir():
            found.append(cls(root, scripts, cls.SCRIPTS))
        return found

    @property
    def name(self) -> str:
        """The package folder name."""
        return self.folder.name

    @property
    def module(self) -> str:
        """The import name: ``swarm_<layer>``, ``swarm_<app>``, the lib name, or ``scripts``."""
        if self.role == self.SCRIPTS:
            return self.SCRIPTS
        if self.role == self.APP:
            return self.PREFIX + self.name.replace("-", "_")
        return self.name.replace("-", "_")

    @property
    def app_name(self) -> str:
        """The app name as written in ``swarm_models.config.<app>``, with underscores."""
        return self.name.replace("-", "_")

    @property
    def source_root(self) -> Path:
        """The folder holding the module, the package's ``src`` or, for the scripts, their own folder."""
        if self.role == self.SCRIPTS:
            return self.folder
        return self.folder / self.SOURCE_FOLDER

    @property
    def module_dir(self) -> Path:
        """The folder of the module itself, such as ``backend/swarm-service/src/swarm_service``."""
        if self.role == self.SCRIPTS:
            return self.folder
        return self.source_root / self.module

    @property
    def pyproject(self) -> Path:
        """The project file of the package."""
        return self.folder / self.PYPROJECT

    @property
    def tests_root(self) -> Path:
        """The central tests folder of the repository."""
        return self.root / self.TESTS_FOLDER

    def python_files(self) -> List[Path]:
        """List the Python files of the module.

        Returns:
            List[Path]: Every ``*.py`` file of the module, sorted, without ``__pycache__`` and hidden folders.
        """
        if not self.module_dir.is_dir():
            return []
        return sorted(path for path in self.module_dir.rglob("*.py") if not self._is_skipped(path))

    def domains(self) -> List[str]:
        """Read the domains an app lists in its project file.

        Returns:
            List[str]: The entries of ``[tool.swarm] domains``, empty when the file or the key is missing.
        """
        if not self.pyproject.is_file():
            return []
        data = tomllib.loads(self.pyproject.read_text(encoding=self.ENCODING))
        tool = data.get(self.TOOL_KEY, {}).get(self.SWARM_KEY, {})
        listed = tool.get(self.DOMAINS_KEY, [])
        return [entry for entry in listed if isinstance(entry, str)]

    def relative(self, path: Path) -> str:
        """Return a path relative to the repository root.

        Args:
            path (Path): The path to convert.

        Returns:
            str: The POSIX path from the repository root.
        """
        return path.relative_to(self.root).as_posix()
