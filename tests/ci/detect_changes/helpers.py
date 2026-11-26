from __future__ import annotations

# Standard library imports
import subprocess
import sys
from pathlib import Path
from typing import Dict, List

ALL_SERVICES = '["alpha","beta"]'
ALL_TYPESCRIPT = '["frontend/apps/ground-control","frontend/packages/config"]'
ALL_IMAGES = '["backend/apps/alpha","frontend/apps/ground-control","frontend/apps/notes"]'
SERVICES_KEY = "services"
TYPESCRIPT_KEY = "typescript"
RUST_KEY = "rust"
REPOSITORY_KEY = "repository"
SPECS_KEY = "specs"
IMAGES_KEY = "images"
RUST_WORKSPACE_PATH = "rust/Cargo.toml"
RUST_CORE_PATH = "rust/core/Cargo.toml"
REPO_FILES: Dict[str, str] = {
    "backend/apps/alpha/pyproject.toml": "[project]\nname = 'alpha'\n",
    "backend/apps/alpha/Dockerfile": "FROM scratch\n",
    "backend/apps/beta/pyproject.toml": "[project]\nname = 'beta'\n",
    "backend/apps/_template/pyproject.toml": "[project]\nname = 'template'\n",
    "backend/apps/.hidden/pyproject.toml": "[project]\nname = 'hidden'\n",
    "backend/apps/README.md": "Apps.\n",
    "frontend/apps/ground-control/package.json": "{}\n",
    "frontend/apps/ground-control/Dockerfile": "FROM scratch\n",
    "frontend/apps/notes/README.md": "Notes.\n",
    "frontend/apps/notes/Dockerfile": "FROM scratch\n",
    "frontend/packages/config/package.json": "{}\n",
    "backend/libs/.gitkeep": "",
}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def script_path() -> Path:
    return repo_root() / ".github" / "scripts" / "detect_changes.py"


def write_repo(root: Path, rust_members: bool = True) -> None:
    files = {
        **REPO_FILES,
        RUST_WORKSPACE_PATH: (
            '[workspace]\nresolver = "2"\n' + ('members = ["core"]\n' if rust_members else "members = []\n")
        ),
    }
    if rust_members:
        files[RUST_CORE_PATH] = "[package]\nname = 'core'\n"
    for relative, content in files.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def run_detector(root: Path, changed: List[str], *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script_path()), "--root", str(root), *args],
        input="\n".join(changed) + "\n",
        capture_output=True,
        text=True,
        check=False,
    )


def outputs(result: subprocess.CompletedProcess[str]) -> Dict[str, str]:
    return dict(line.split("=", 1) for line in result.stdout.splitlines())
