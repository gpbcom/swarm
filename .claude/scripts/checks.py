#!/usr/bin/env python3
"""Run every applicable check of a ticket deterministically, save the evidence, and print the verdict as JSON.

Usage, from the repository root, on the ticket branch:
    python3 .claude/scripts/checks.py --ticket T0.01 [--base develop]

Which checks apply is decided here, never by a model (TKT-6): a check whose target does not exist yet (a Cargo
workspace with no member crate, no TypeScript workspace package, no Python source for mypy) is reported under
``not_applicable`` with its reason. Only project code is checked with the AGENT.md tools (``services/``, ``packages/``,
``frontends/``, ``tests/``, ``deploy/``); ``.claude/`` and ``docs/`` are covered by ``specs.py check``, which always
runs, with ``ticket_refs.py check`` (TICKET.md, PLAN.md and PROGRESS.md refer to the specification, TKT-2) and
``plan.py check`` (the readable view of PLAN.md is up to date). Each check's output is saved to ``docs/tickets/<ID>/tests-evidences/<check>.txt``. The last line printed is
the JSON verdict: ``{"passed": bool, "failures": [{"check", "file", "detail", "environment"}], "not_applicable": [...], "passed_checks": [...]}``.
A failure with ``environment: true`` comes from a missing tool or module, not from the code.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Union

ROOT = Path(__file__).resolve().parents[2]
PROJECT_PREFIXES = ("services/", "packages/", "frontends/", "tests/", "deploy/")
TIMEOUT_S = 900
# A failure whose output holds one of these is caused by the environment (a missing tool or module), not by the
# ticket's code: fixer agents cannot repair it, so the run stops and the person fixes the environment (TKT-6).
ENVIRONMENT_MARKERS = ("ModuleNotFoundError", "No module named", "command not found")


def run(command: List[str], cwd: Path = ROOT) -> Tuple[int, str]:
    try:
        result = subprocess.run(command, cwd=cwd, capture_output=True, text=True, timeout=TIMEOUT_S, check=False)
        return result.returncode, (result.stdout + result.stderr).strip()
    except FileNotFoundError as error:
        return 127, f"command not found: {error.filename}"
    except subprocess.TimeoutExpired:
        return 124, f"timed out after {TIMEOUT_S} s"


def changed_files(base: str) -> List[str]:
    code, out = run(["git", "diff", "--name-only", f"{base}...HEAD"])
    return [line for line in out.splitlines() if line] if code == 0 else []


class Checks:
    def __init__(self, ticket: str) -> None:
        self.evidence = ROOT / "docs" / "tickets" / ticket / "tests-evidences"
        self.evidence.mkdir(parents=True, exist_ok=True)
        self.failures: List[Dict[str, Union[str, bool]]] = []
        self.not_applicable: List[str] = []
        self.passed: List[str] = []

    def check(self, name: str, command: List[str], file: str, cwd: Path = ROOT) -> bool:
        code, out = run(command, cwd)
        slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
        (self.evidence / f"{slug}.txt").write_text(f"$ {' '.join(command)}\n(cwd {cwd.relative_to(ROOT) or '.'})\n\n{out}\n", encoding="utf-8")
        if code == 0:
            self.passed.append(name)
            return True
        detail = "\n".join(out.splitlines()[-12:])
        environment = code == 127 or any(marker in out for marker in ENVIRONMENT_MARKERS)
        self.failures.append({"check": name, "file": file, "detail": detail[:1500], "environment": environment})
        return False

    def skip(self, name: str, reason: str) -> None:
        self.not_applicable.append(f"{name}: {reason}")


def python_checks(checks: Checks, changed: List[str]) -> None:
    files = [f for f in changed if f.endswith(".py") and f.startswith(PROJECT_PREFIXES) and (ROOT / f).exists()]
    if not files:
        checks.skip("python", "no Python project file changed")
        return
    checks.check("ruff check", ["uv", "run", "ruff", "check", *files], files[0])
    checks.check("ruff format", ["uv", "run", "ruff", "format", "--check", *files], files[0])
    sources = sorted(str(p.relative_to(ROOT)) for pattern in ("services/*/src", "packages/python/*/src") for p in ROOT.glob(pattern))
    if sources:
        checks.check("mypy", ["uv", "run", "mypy", *sources], sources[0])
    else:
        checks.skip("mypy", "no services/*/src or packages/python/*/src yet")
    checks.check("pytest", ["uv", "run", "pytest", "-q"], "tests")


def rust_checks(checks: Checks, changed: List[str]) -> None:
    manifest = ROOT / "packages" / "rust" / "Cargo.toml"
    if not any(f.startswith("packages/rust/") for f in changed) or not manifest.exists():
        checks.skip("rust", "no Rust change")
        return
    checks.check("cargo metadata", ["cargo", "metadata", "--no-deps", "--format-version", "1", "--locked",
                                     "--manifest-path", str(manifest)], "packages/rust/Cargo.toml")
    members = re.search(r"members\s*=\s*\[(.*?)\]", manifest.read_text(encoding="utf-8"), re.S)
    if not members or not members.group(1).strip():
        for name in ("cargo fmt", "cargo clippy", "cargo test"):
            checks.skip(name, "the Cargo workspace has no member crate yet")
        return
    cwd = manifest.parent
    checks.check("cargo fmt", ["cargo", "fmt", "--all", "--check"], "packages/rust", cwd)
    checks.check("cargo clippy", ["cargo", "clippy", "--workspace", "--all-targets", "--", "-D", "warnings"], "packages/rust", cwd)
    checks.check("cargo test", ["cargo", "test", "--workspace"], "packages/rust", cwd)


def typescript_checks(checks: Checks, changed: List[str]) -> None:
    if not any(f.startswith(("frontends/", "packages/ts/")) or f in ("package.json", "pnpm-workspace.yaml", "turbo.json") for f in changed):
        checks.skip("typescript", "no TypeScript change")
        return
    packages = [p for pattern in ("frontends/*/package.json", "packages/ts/*/package.json") for p in ROOT.glob(pattern)]
    if not packages:
        for name in ("eslint", "tsc", "vitest"):
            checks.skip(name, "no TypeScript workspace package yet")
        checks.check("pnpm install", ["pnpm", "install", "--frozen-lockfile"], "pnpm-lock.yaml")
        return
    checks.check("pnpm install", ["pnpm", "install", "--frozen-lockfile"], "pnpm-lock.yaml")
    checks.check("lint", ["pnpm", "-r", "--if-present", "lint"], "frontends")
    checks.check("typecheck", ["pnpm", "-r", "--if-present", "typecheck"], "frontends")
    checks.check("test", ["pnpm", "-r", "--if-present", "test"], "frontends")


def terraform_checks(checks: Checks, changed: List[str]) -> None:
    tf = [f for f in changed if f.startswith("deploy/terraform/") and f.endswith((".tf", ".tftest.hcl"))]
    if not tf:
        checks.skip("terraform", "no Terraform change")
        return
    checks.check("terraform fmt", ["terraform", "fmt", "-check", "-recursive", "deploy/terraform"], "deploy/terraform")
    folders = sorted({str(Path(f).parent) if not f.endswith(".tftest.hcl") else str(Path(f).parent.parent) for f in tf})
    for folder in folders:
        path = ROOT / folder
        if not list(path.glob("*.tf")):
            continue
        if not checks.check(f"terraform init {folder}", ["terraform", "init", "-backend=false", "-input=false"], folder, path):
            continue
        checks.check(f"terraform validate {folder}", ["terraform", "validate"], folder, path)
        if (path / "tests").is_dir():
            checks.check(f"terraform test {folder}", ["terraform", "test"], folder, path)


def main() -> int:
    args = sys.argv[1:]
    ticket = args[args.index("--ticket") + 1] if "--ticket" in args else ""
    base = args[args.index("--base") + 1] if "--base" in args else "develop"
    if not re.fullmatch(r"T\d\.\d\d", ticket):
        print(__doc__, file=sys.stderr)
        return 2
    checks = Checks(ticket)
    changed = changed_files(base)
    python_checks(checks, changed)
    rust_checks(checks, changed)
    typescript_checks(checks, changed)
    terraform_checks(checks, changed)
    checks.check("specs check", ["python3", ".claude/skills/write-specs/scripts/specs.py", "check"], "docs/specs")
    folder = f"docs/tickets/{ticket}"
    checks.check("ticket refs", ["python3", ".claude/scripts/ticket_refs.py", "check", "--ticket", ticket], folder)
    if (ROOT / folder / "PLAN.md").is_file():
        checks.check("plan view", ["python3", ".claude/scripts/plan.py", "check", "--ticket", ticket], f"{folder}/PLAN.md")
    verdict = {"passed": not checks.failures, "failures": checks.failures,
               "not_applicable": checks.not_applicable, "passed_checks": checks.passed}
    print(json.dumps(verdict))
    return 0 if not checks.failures else 1


if __name__ == "__main__":
    sys.exit(main())
