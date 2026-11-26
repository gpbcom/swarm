from __future__ import annotations

# Standard library imports
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict


def repo_root() -> Path:
    """Return the repository root."""
    return Path(__file__).resolve().parents[2]


def services_root() -> Path:
    """Return the folder holding the services to check.

    The variable ``SWARM_CONVENTIONS_SERVICES_ROOT`` overrides the default ``services/`` folder.
    """
    override = os.environ.get("SWARM_CONVENTIONS_SERVICES_ROOT")
    if override:
        return Path(override)
    return repo_root() / "services"


def packages_root() -> Path:
    """Return the folder holding the shared Python packages to check.

    The variable ``SWARM_CONVENTIONS_PACKAGES_ROOT`` overrides the default ``packages/python/`` folder.
    """
    override = os.environ.get("SWARM_CONVENTIONS_PACKAGES_ROOT")
    if override:
        return Path(override)
    return repo_root() / "packages" / "python"


def libs_root() -> Path:
    """Return the folder holding the kernel libraries of the target layout.

    The variable ``SWARM_CONVENTIONS_LIBS_ROOT`` overrides the default ``backend/libs/`` folder.
    """
    override = os.environ.get("SWARM_CONVENTIONS_LIBS_ROOT")
    if override:
        return Path(override)
    return repo_root() / "backend" / "libs"


def layers_root() -> Path:
    """Return the folder holding the layer packages of the target layout.

    The variable ``SWARM_CONVENTIONS_LAYERS_ROOT`` overrides the default ``backend/`` folder.
    """
    override = os.environ.get("SWARM_CONVENTIONS_LAYERS_ROOT")
    if override:
        return Path(override)
    return repo_root() / "backend"


def write_files(root: Path, files: Dict[str, str]) -> None:
    """Write each relative POSIX path of ``files`` under ``root`` with its content."""
    for relative, content in files.items():
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")


def run_convention_tests(services_root: Path) -> subprocess.CompletedProcess[str]:
    """Run the convention tests against the services found under ``services_root``."""
    env = os.environ.copy()
    env["SWARM_CONVENTIONS_SERVICES_ROOT"] = str(services_root)
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "tests/conventions/services/test_service_conventions.py",
            "-q",
            "-p",
            "no:cacheprovider",
        ],
        check=False,
        cwd=repo_root(),
        capture_output=True,
        text=True,
        env=env,
    )
