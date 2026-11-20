from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path
from typing import List

REPO_ROOT = Path(__file__).resolve().parents[3]
SKILL_RELATIVE = Path(".claude/skills/write-specs")
SPECS_RELATIVE = Path("docs/specs")
SCRIPT_RELATIVE = SKILL_RELATIVE / "scripts" / "specs.py"
MOCKUP_CSS_RELATIVE = SPECS_RELATIVE / "screens" / "mockups" / "visual-identity.css"
IDENTITY_RELATIVE = SPECS_RELATIVE / "visual-identity.md"
TOKENS_DIR_RELATIVE = Path("packages/ts/tokens/src")
TOKENS_CSS_RELATIVE = TOKENS_DIR_RELATIVE / "tokens.css"
BUILD = "build"
CHECK = "check"
ENCODING = "utf-8"


def copy_project(destination: Path) -> Path:
    """Copy the write-specs skill and the specifications into destination, keeping their relative paths."""
    shutil.copytree(
        REPO_ROOT / SKILL_RELATIVE,
        destination / SKILL_RELATIVE,
        ignore=shutil.ignore_patterns("__pycache__"),
    )
    shutil.copytree(REPO_ROOT / SPECS_RELATIVE, destination / SPECS_RELATIVE)
    return destination


def run_specs(root: Path, command: str) -> subprocess.CompletedProcess[str]:
    """Run ``specs.py <command>`` of the copied tree, from its root."""
    return subprocess.run(
        [sys.executable, str(root / SCRIPT_RELATIVE), command],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )


def output_lines(result: subprocess.CompletedProcess[str]) -> List[str]:
    """Return every line printed on standard output and standard error."""
    return (result.stdout + result.stderr).splitlines()


def tokens_lines(root: Path) -> List[str]:
    """Return the lines ``check`` prints that mention the generated tokens file."""
    return [line for line in output_lines(run_specs(root, CHECK)) if TOKENS_CSS_RELATIVE.as_posix() in line]
