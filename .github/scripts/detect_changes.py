"""Detect which parts of the repository a change touches (T0.04, step 1 of the CI/CD).

Usage:
    python3 .github/scripts/detect_changes.py [--root <repo root>] [--all]

The changed paths are read from stdin, one POSIX path per line, relative to the root. ``--all`` does not read stdin and
selects everything that applies. It prints exactly five lines, then exits 0:

    services=<JSON array of service names>
    typescript=<JSON array of front end and TypeScript package folders>
    rust=<true|false>
    repository=<true|false>
    specs=<true|false>

An unknown argument, or ``--root`` without a value, prints a usage line on stderr and exits 2.
"""

from __future__ import annotations

import json
import sys
import tomllib
from pathlib import Path
from typing import List, Optional, Set, Tuple

SHARED_PREFIXES = ("packages/", ".github/scripts/")
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
    }
)
REPOSITORY_PREFIXES = ("tests/", ".claude/")
SPECS_PREFIXES = ("docs/specs/", ".claude/skills/write-specs/")
USAGE = "usage: detect_changes.py [--root <repo root>] [--all]"


def discover_services(root: Path) -> List[str]:
    """List the services: direct sub-folders of ``services`` not starting with ``.`` or ``_``."""
    folder = root / "services"
    if not folder.is_dir():
        return []
    return sorted(p.name for p in folder.iterdir() if p.is_dir() and not p.name.startswith((".", "_")))


def discover_typescript(root: Path) -> List[str]:
    """List the ``frontends/<name>`` and ``packages/ts/<name>`` folders holding a ``package.json``."""
    found: List[str] = []
    for parent in ("frontends", "packages/ts"):
        folder = root / parent
        if not folder.is_dir():
            continue
        for child in folder.iterdir():
            if child.is_dir() and (child / "package.json").is_file():
                found.append(f"{parent}/{child.name}")
    return sorted(found)


def rust_applies(root: Path) -> bool:
    """Tell whether the Rust workspace exists and has at least one member."""
    manifest = root / "packages" / "rust" / "Cargo.toml"
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
    """Print the five output lines for the changed paths on stdin."""
    parsed = parse_args(sys.argv[1:] if argv is None else argv)
    if parsed is None:
        print(USAGE, file=sys.stderr)
        return 2
    root, select_all = parsed
    all_services = discover_services(root)
    all_typescript = discover_typescript(root)

    services: Set[str] = set()
    typescript: Set[str] = set()
    rust = repository = specs = False
    everything = select_all
    paths = [] if select_all else read_paths(sys.stdin.read())
    for path in paths:
        if is_shared(path):
            everything = True
            continue
        parts = path.split("/")
        if parts[0] == "services" and len(parts) > 2 and parts[1] in all_services:
            services.add(parts[1])
        elif parts[0] == "frontends" and len(parts) > 2 and f"frontends/{parts[1]}" in all_typescript:
            typescript.add(f"frontends/{parts[1]}")
        if path.startswith(REPOSITORY_PREFIXES):
            repository = True
        if path.startswith(SPECS_PREFIXES):
            specs = True
    if everything:
        services = set(all_services)
        typescript = set(all_typescript)
        rust = rust_applies(root)
        repository = specs = True

    print(f"services={json.dumps(sorted(services), separators=(',', ':'))}")
    print(f"typescript={json.dumps(sorted(typescript), separators=(',', ':'))}")
    print(f"rust={str(rust).lower()}")
    print(f"repository={str(repository).lower()}")
    print(f"specs={str(specs).lower()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
