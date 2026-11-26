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


def write_files(root: Path, files: Dict[str, str]) -> None:
    """Write each relative POSIX path of ``files`` under ``root`` with its content."""
    for relative, content in files.items():
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")


def run_convention_tests(root: Path) -> subprocess.CompletedProcess[str]:
    """Run the code convention tests of the backend against the packages found under the repository ``root``."""
    env = os.environ.copy()
    env["SWARM_CONVENTIONS_BACKEND_ROOT"] = str(root)
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "tests/conventions/backend/test_backend_conventions.py",
            "-k",
            "test_every_code_rule_holds_for_every_package",
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
