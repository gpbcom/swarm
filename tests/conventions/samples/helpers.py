from __future__ import annotations

from pathlib import Path
from typing import Dict

from tests.conventions.helpers import write_files


def write_broken_service(services_root: Path) -> Path:
    """Write the sample service ``broken``, which breaks each convention rule exactly once.

    The breaks are: ``api/routes.py`` imports from ``storage`` (layer_imports), ``service/two_classes.py`` holds two
    classes (one_class_per_file), ``service/crowded/`` holds six modules (five_files_per_folder),
    ``service/typed.py`` imports ``Any`` (no_any), ``service/nested.py`` nests a function (no_nested_function),
    ``service/job.py`` has ``run`` without a base class (lifecycle_base_classes) and ``service/customer.py`` holds a
    Pydantic model outside ``models`` (pydantic_models_in_models).
    """
    root = services_root / "broken"
    package = "src/broken"
    files: Dict[str, str] = {
        "pyproject.toml": '[project]\nname = "broken"\nversion = "0.1.0"\n',
        f"{package}/__init__.py": "",
        f"{package}/api/__init__.py": "",
        f"{package}/service/__init__.py": "",
        f"{package}/storage/__init__.py": "",
        f"{package}/clients/__init__.py": "",
        f"{package}/models/__init__.py": "",
        f"{package}/api/routes.py": (
            "from __future__ import annotations\n\n"
            "from broken.storage.store import Store\n\n\n"
            "def read() -> Store:\n    return Store()\n"
        ),
        f"{package}/storage/store.py": "from __future__ import annotations\n\n\nclass Store:\n    pass\n",
        f"{package}/service/two_classes.py": (
            "from __future__ import annotations\n\n\nclass First:\n    pass\n\n\nclass Second:\n    pass\n"
        ),
        f"{package}/service/typed.py": (
            "from __future__ import annotations\n\nfrom typing import Any\n\n\n"
            "def echo(value: Any) -> None:\n    return None\n"
        ),
        f"{package}/service/nested.py": (
            "from __future__ import annotations\n\n\n"
            "def outer() -> None:\n    def inner() -> None:\n        return None\n\n    inner()\n"
        ),
        f"{package}/service/job.py": (
            "from __future__ import annotations\n\n\nclass Job:\n    def run(self) -> None:\n        return None\n"
        ),
        f"{package}/service/customer.py": (
            "from __future__ import annotations\n\nfrom pydantic import BaseModel\n\n\n"
            "class Customer(BaseModel):\n    name: str = 'x'\n"
        ),
        f"{package}/service/crowded/__init__.py": "",
    }
    for index in range(1, 7):
        files[f"{package}/service/crowded/module_{index}.py"] = (
            f"from __future__ import annotations\n\n\ndef work_{index}() -> None:\n    return None\n"
        )
    write_files(root, files)
    return root
