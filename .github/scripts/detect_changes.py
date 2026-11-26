from __future__ import annotations

import json
import sys
import tomllib
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

SHARED_PREFIXES = (
    ".github/scripts/",
    "rust/",
    "scripts/",
    "frontend/packages/",
    "qa/e2e/",
    "backend/libs/",
)
SHARED_NAMES = frozenset({"uv.lock", "pnpm-lock.yaml", "Cargo.lock"})
SHARED_FILES = frozenset(
    {
        "pyproject.toml",
        "package.json",
        "pnpm-workspace.yaml",
        "turbo.json",
        ".github/workflows/ci.yml",
        ".github/workflows/python.yml",
        ".github/workflows/rust.yml",
        ".github/workflows/typescript.yml",
        ".github/workflows/specs.yml",
        ".github/workflows/images.yml",
        "infra/compose/e2e.yaml",
        ".dockerignore",
    }
)
REPOSITORY_PREFIXES = ("tests/", ".claude/")
SPECS_PREFIXES = ("docs/specs/", ".claude/skills/write-specs/")
LAYER_PACKAGES = frozenset({"swarm-models", "swarm-storage", "swarm-clients", "swarm-service", "swarm-api"})
SHARED_DOMAIN = "shared"
API_PACKAGE = "swarm-api"
API_VERSION = "v1"
API_SHARED_DOMAINS = frozenset({"live"})
USAGE = "usage: detect_changes.py [--root <repo root>] [--all]"


def discover_apps(root: Path) -> Dict[str, List[str]]:
    """Map each ``backend/apps/<app>`` to the domains of its ``[tool.swarm] domains``."""
    folder = root / "backend" / "apps"
    found: Dict[str, List[str]] = {}
    if not folder.is_dir():
        return found
    for child in sorted(folder.iterdir()):
        manifest = child / "pyproject.toml"
        if not child.is_dir() or child.name.startswith((".", "_")) or not manifest.is_file():
            continue
        try:
            with manifest.open("rb") as handle:
                data = tomllib.load(handle)
        except (OSError, tomllib.TOMLDecodeError):
            data = {}
        domains = data.get("tool", {}).get("swarm", {}).get("domains", [])
        found[child.name] = [d for d in domains if isinstance(d, str)] if isinstance(domains, list) else []
    return found


def apps_of_layer_path(parts: List[str], apps: Dict[str, List[str]]) -> Optional[Set[str]]:
    """Return the apps a ``backend/swarm-<layer>/...`` path selects, or None when it is no such path.

    In ``swarm-api``, the domain is the folder under ``v1/``; its other folders (handlers, middlewares, ``Depends``
    providers) and the shared ``v1/live`` serve every app.
    """
    if len(parts) < 3 or parts[0] != "backend" or parts[1] not in LAYER_PACKAGES:
        return None
    if parts[1] == API_PACKAGE and parts[2] == "src" and len(parts) > 5:
        if parts[4] != API_VERSION or parts[5] in API_SHARED_DOMAINS:
            return set(apps)
        domain = parts[5]
    elif parts[2] == "src" and len(parts) > 4:
        domain = parts[4]
    elif parts[2] == "tests" and len(parts) > 4:
        domain = parts[3]
    else:
        return set(apps)
    if domain == SHARED_DOMAIN:
        return set(apps)
    return {name for name, domains in apps.items() if domain in domains}


def discover_typescript(root: Path) -> List[str]:
    """List the front-end app and package folders holding a ``package.json``."""
    found: List[str] = []
    for parent in ("frontend/apps", "frontend/packages"):
        folder = root / parent
        if not folder.is_dir():
            continue
        for child in folder.iterdir():
            if child.is_dir() and (child / "package.json").is_file():
                found.append(f"{parent}/{child.name}")
    return sorted(found)


def discover_images(root: Path) -> List[str]:
    """List the image folders (backend apps and front-end apps) holding a ``Dockerfile``."""
    found: List[str] = []
    for parent in ("backend/apps", "frontend/apps"):
        folder = root / parent
        if not folder.is_dir():
            continue
        for child in folder.iterdir():
            if child.is_dir() and not child.name.startswith((".", "_")) and (child / "Dockerfile").is_file():
                found.append(f"{parent}/{child.name}")
    return sorted(found)


def rust_applies(root: Path) -> bool:
    """Tell whether the Rust workspace ``rust/`` exists and has at least one member."""
    manifest = root / "rust" / "Cargo.toml"
    if not manifest.is_file():
        return False
    try:
        with manifest.open("rb") as handle:
            data = tomllib.load(handle)
    except (OSError, tomllib.TOMLDecodeError):
        return False
    workspace = data.get("workspace")
    if not isinstance(workspace, dict):
        return False
    members = workspace.get("members")
    return isinstance(members, list) and len(members) > 0


def is_shared(path: str) -> bool:
    """Tell whether a changed path selects everything that applies."""
    return path in SHARED_FILES or path.rsplit("/", 1)[-1] in SHARED_NAMES or path.startswith(SHARED_PREFIXES)


def read_paths(text: str) -> List[str]:
    """Split stdin into paths, ignoring blank lines and surrounding spaces."""
    return [line.strip() for line in text.splitlines() if line.strip()]


def parse_args(argv: List[str]) -> Optional[Tuple[Path, bool]]:
    """Read the arguments, returning the root and the ``--all`` flag, or None when they are bad."""
    root = Path(__file__).resolve().parents[2]
    select_all = False
    index = 0
    while index < len(argv):
        argument = argv[index]
        if argument == "--all":
            select_all = True
        elif argument == "--root" and index + 1 < len(argv):
            index += 1
            root = Path(argv[index])
        else:
            return None
        index += 1
    return root, select_all


def main(argv: Optional[List[str]] = None) -> int:
    """Print the six output lines for the changed paths on stdin."""
    parsed = parse_args(sys.argv[1:] if argv is None else argv)
    if parsed is None:
        print(USAGE, file=sys.stderr)
        return 2
    root, select_all = parsed
    all_typescript = discover_typescript(root)
    all_images = discover_images(root)
    apps = discover_apps(root)

    services: Set[str] = set()
    typescript: Set[str] = set()
    images: Set[str] = set()
    rust = repository = specs = False
    everything = select_all
    paths = [] if select_all else read_paths(sys.stdin.read())
    for path in paths:
        if is_shared(path):
            everything = True
            continue
        parts = path.split("/")
        owners = apps_of_layer_path(parts, apps)
        if owners is not None:
            services |= owners
            images |= {f"backend/apps/{name}" for name in owners if f"backend/apps/{name}" in all_images}
            repository = True
            continue
        if parts[0] == "backend" and len(parts) > 3 and parts[1] == "apps" and parts[2] in apps:
            services.add(parts[2])
        elif parts[0] == "frontend" and len(parts) > 3 and f"frontend/{parts[1]}/{parts[2]}" in all_typescript:
            typescript.add(f"frontend/{parts[1]}/{parts[2]}")
        if len(parts) > 3 and f"{parts[0]}/{parts[1]}/{parts[2]}" in all_images:
            images.add(f"{parts[0]}/{parts[1]}/{parts[2]}")
        if path.startswith(REPOSITORY_PREFIXES):
            repository = True
        if path.startswith(SPECS_PREFIXES):
            specs = True
    if everything:
        services = set(apps)
        typescript = set(all_typescript)
        images = set(all_images)
        rust = rust_applies(root)
        repository = specs = True

    print(f"services={json.dumps(sorted(services), separators=(',', ':'))}")
    print(f"typescript={json.dumps(sorted(typescript), separators=(',', ':'))}")
    print(f"rust={str(rust).lower()}")
    print(f"repository={str(repository).lower()}")
    print(f"specs={str(specs).lower()}")
    print(f"images={json.dumps(sorted(images), separators=(',', ':'))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
