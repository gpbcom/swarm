#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "skills" / "ticket" / "scripts"))

from check_ticket import has_no_screen_reason, screens_of, screens_section, touches_front_end

USAGE = """Run every applicable check of a ticket deterministically, save the evidence, and print the verdict as JSON.

Usage, from the repository root, on the ticket branch:
    python3 .claude/scripts/tickets/checks.py --ticket T0.01 [--base develop]

Which checks apply is decided here, never by a model (TKT-6): a check whose target does not exist yet (a Cargo
workspace with no member crate, no TypeScript workspace package, no Python source for mypy) is reported under
``not_applicable`` with its reason. Only project code is checked with the AGENT.md tools (``services/``, ``packages/``,
``frontend/apps/``, ``tests/``, ``infra/``); ``.claude/`` and ``docs/`` are covered by ``specs.py check``, which always
runs, with ``ticket_refs.py check`` (TICKET.md, PLAN.md and PROGRESS.md refer to the specification, TKT-2) and
``plan.py check`` (the readable view of PLAN.md is up to date). Each check's output is saved to ``docs/tickets/<ID>/tests-evidences/<check>.txt``. The last line printed is
the JSON verdict: ``{"passed": bool, "failures": [{"check", "file", "detail", "environment"}], "not_applicable": [...], "passed_checks": [...]}``.
A failure with ``environment: true`` comes from a missing tool or module, not from the code.

Several tickets share the main checkout (TKT-16), and the AGENT.md tools read a whole workspace (``uv`` the
``services/*`` glob, ``pnpm -r`` every package), so another ticket's half-built work would fail this one. When the
ticket has recorded its own files, every check runs in a clean temporary worktree of ``HEAD`` holding only the
ticket's own changes (TKT-6), removed afterwards; the evidence is still written to the ticket's folder.
"""

ROOT = Path(__file__).resolve().parents[3]
PROJECT_PREFIXES = ("services/", "packages/", "frontend/apps/", "tests/", "infra/")
TIMEOUT_S = 900
# A failure whose output holds one of these is caused by the environment (a missing tool or module), not by the
# ticket's code: fixer agents cannot repair it, so the run stops and the person fixes the environment (TKT-6).
ENVIRONMENT_MARKERS = ("command not found",)
# A missing module is the environment's fault only when it is not the project's own code: ``No module named
# 'tests.api'`` or ``'swarm_rest'`` is a wrong import or a wrong path in the ticket, which its owner fixes (L-28).
MISSING_MODULE = re.compile(r"No module named '([^']+)'")


def run(command: List[str], cwd: Path = ROOT, env: Optional[Dict[str, str]] = None) -> Tuple[int, str]:
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=TIMEOUT_S,
            check=False,
            env={**os.environ, **env} if env else None,
        )
        return result.returncode, (result.stdout + result.stderr).strip()
    except FileNotFoundError as error:
        return 127, f"command not found: {error.filename}"
    except subprocess.TimeoutExpired:
        return 124, f"timed out after {TIMEOUT_S} s"


def first_party(module: str, root: Path = ROOT) -> bool:
    """Tell whether a module name belongs to the repository: its tests, a service or a Python package."""
    top = module.split(".")[0]
    if top in ("tests", "conftest") or (root / top).exists():
        return True
    return any(root.glob(f"services/*/src/{top}")) or any(root.glob(f"packages/python/*/src/{top}")) or any(root.glob(f"backend/libs/*/src/{top}"))


def environment_failure(code: int, out: str, root: Path = ROOT) -> bool:
    """Tell whether a failed check comes from the environment (a missing tool or third-party module), not the code."""
    if code == 127 or any(marker in out for marker in ENVIRONMENT_MARKERS):
        return True
    missing = MISSING_MODULE.findall(out)
    # L-34 c: the clean tree holds only the ticket's files, so a module of the project that exists in the main
    # checkout is a wrong import or a missing file of the ticket, never the environment.
    return bool(missing) and not any(first_party(name, root) or first_party(name, ROOT) for name in missing)


def own_paths(ticket: str, root: Path = ROOT) -> Optional[List[str]]:
    """Return the files and folders the ticket recorded as its own (TKT-16), or None when it recorded none."""
    if not ticket:
        return None
    _, common = run(["git", "rev-parse", "--path-format=absolute", "--git-common-dir"], cwd=root)
    state = Path(common.strip()) / "swarm" / ticket / "state.json"
    paths = json.loads(state.read_text(encoding="utf-8")).get("paths") if state.is_file() else None
    return [str(path) for path in paths] if isinstance(paths, list) else None


def isolated_tree(changed: List[str], root: Path = ROOT) -> Path:
    """Make a clean worktree of ``HEAD`` holding only the given changes of ``root``, and return its folder.

    Every other ticket's uncommitted work stays out (L-22): each changed file is copied from ``root``, and a changed
    file that no longer exists there is deleted. The caller removes the tree with ``remove_tree``.
    """
    tree = Path(tempfile.mkdtemp(prefix="swarm-checks-"))
    code, out = run(["git", "worktree", "add", "--detach", "--force", str(tree), "HEAD"], cwd=root)
    if code != 0:
        shutil.rmtree(tree, ignore_errors=True)
        raise RuntimeError(f"Could not make the clean worktree for the checks: {out}")
    for name in changed:
        source, target = root / name, tree / name
        if source.is_file():
            target.parent.mkdir(parents=True, exist_ok=True)
            # L-39: a fresh modification time, never the source's (copy2): cargo shares the main checkout's target
            # folder and judges freshness by time, so an older copied source would reuse another tree's stale build.
            shutil.copy(source, target)
        elif target.is_file() or target.is_symlink():
            target.unlink()
    return tree


def remove_tree(tree: Path, root: Path = ROOT) -> None:
    """Remove a worktree made by ``isolated_tree``, whatever its state."""
    run(["git", "worktree", "remove", "--force", str(tree)], cwd=root)
    shutil.rmtree(tree, ignore_errors=True)
    run(["git", "worktree", "prune"], cwd=root)


def changed_files(base: str, ticket: str = "", root: Path = ROOT) -> List[str]:
    # The ticket's work stays uncommitted until the ticket is done (TKT-5): compare the working tree, untracked files
    # included, with the point where the branch left the base. Several tickets share the checkout (TKT-16): when the
    # ticket recorded its own files, only those are checked, so another ticket's half-done work never fails it.
    code, merge_base = run(["git", "merge-base", base, "HEAD"], cwd=root)
    if code != 0:
        return []
    _, tracked = run(["git", "diff", "--name-only", merge_base.strip()], cwd=root)
    _, untracked = run(["git", "ls-files", "--others", "--exclude-standard"], cwd=root)
    found = sorted({line for line in f"{tracked}\n{untracked}".splitlines() if line})
    own = own_paths(ticket, root)
    if own is None:
        return found
    return [name for name in found if any(name == path or name.startswith(path.rstrip("/") + "/") for path in own)]


SCREENSHOT = "📸 Screenshot"
PIPELINE_TICKET = "T0.20"


def screen_problems(
    root: Path, ticket: str, changed: List[str], pipeline_ready: bool
) -> Tuple[List[Tuple[str, str]], Optional[str]]:
    """Return the screens of a front-end ticket that are not captured yet, as (file, detail), or why none applies.

    TKT-21: a ticket that changes a front end lists the screens it shows; once the screenshot pipeline of T0.20 is
    merged, each of them must be a 📸 Screenshot on its use case page, captured in light and dark mode by the ticket
    itself (both PNGs among its changed files), with its mock-up deleted.
    """
    ticket_md = root / "docs" / "tickets" / ticket / "TICKET.md"
    if not ticket_md.is_file() or not touches_front_end(ticket, root):
        return [], "the ticket changes no front end"
    body = screens_section(ticket_md.read_text(encoding="utf-8"))
    screens = screens_of(body)
    if not screens:
        reason = "the ticket says '➖ No screen' in TICKET.md" if has_no_screen_reason(body) else "no screen is listed"
        return [], reason
    if not pipeline_ready:
        return [], f"the screenshot pipeline of {PIPELINE_TICKET} is not merged yet: the screens stay mock-ups"
    failures: List[Tuple[str, str]] = []
    for use_case, node in screens:
        light = f"docs/specs/screens/{use_case}/{node}.png"
        dark = f"docs/specs/screens/{use_case}/{node}.dark.png"
        pages = sorted((root / "docs" / "specs" / "functional" / "use-cases").glob(f"{use_case}-*.md"))
        rows = [
            line
            for page in pages
            for line in page.read_text(encoding="utf-8").splitlines()
            if f'<a id="screen-{node}"></a>' in line
        ]
        if not rows or SCREENSHOT not in rows[0]:
            failures.append(
                (
                    light,
                    (
                        f"{use_case} {node} is still a mock-up on its use case page: capture it from the "
                        f"app in light and dark mode and set its source to {SCREENSHOT} (TKT-21)."
                    ),
                )
            )
            continue
        for png in (light, dark):
            if png not in changed:
                failures.append((png, f"{use_case} {node}: {png} was not captured by this ticket (TKT-21)."))
        mockup = root / "docs" / "specs" / "screens" / "mockups" / use_case / f"{node}.html"
        if mockup.is_file():
            failures.append((str(mockup.relative_to(root)), f"{use_case} {node} is a screenshot: delete its mock-up."))
    return failures, None


FAILING_FILES_MAX = 10
# L-39: ``swarm_core`` is a PyO3 wheel built by maturin, outside the uv workspace, so ``uv run`` never puts it in the
# clean tree's fresh environment. When Python code of the tree imports it, the checks build the wheel and install it there.
SWARM_CORE_IMPORT = re.compile(r"^\s*(?:from|import)\s+swarm_core\b", re.MULTILINE)
SWARM_CORE_MANIFEST = "rust/swarm-core/python/Cargo.toml"
PRINTED_PATH = re.compile(r"[\w.\-]+(?:/[\w.\-]+)+")
MYPY_SOURCE_GLOBS = ("services/*/src", "packages/python/*/src", "backend/**/src")
PYTHON_GLOBS = ("services/*/src/**/*.py", "services/*/tests/**/*.py", "tests/**/*.py")


def imports_swarm_core(root: Path) -> bool:
    """Tell whether a Python file of a service or of the root ``tests/`` imports the ``swarm_core`` wheel."""
    for pattern in PYTHON_GLOBS:
        for path in root.glob(pattern):
            if SWARM_CORE_IMPORT.search(path.read_text(encoding="utf-8", errors="replace")):
                return True
    return False


def install_swarm_core(checks: Checks) -> None:
    """Build the ``swarm_core`` wheel from the tree's Rust sources and install it in the tree's own environment (L-39)."""
    root = checks.root
    if not (root / SWARM_CORE_MANIFEST).is_file() or not imports_swarm_core(root):
        checks.skip("swarm_core wheel", "no Python code imports swarm_core")
        return
    dist = Path(tempfile.mkdtemp(prefix="swarm-core-wheel-"))
    target = {"CARGO_TARGET_DIR": str(ROOT / "rust" / "target")}
    try:
        built = checks.check(
            "swarm_core wheel",
            ["uv", "run", "maturin", "build", "--release", "--manifest-path", SWARM_CORE_MANIFEST, "--out", str(dist)],
            SWARM_CORE_MANIFEST,
            env=target,
        )
        wheels = sorted(dist.glob("swarm_core-*.whl"))
        if built and wheels:
            checks.check(
                "swarm_core install",
                [
                    "uv",
                    "pip",
                    "install",
                    "--no-deps",
                    "--python",
                    str(root / ".venv" / "bin" / "python"),
                    str(wheels[-1]),
                ],
                SWARM_CORE_MANIFEST,
            )
    finally:
        shutil.rmtree(dist, ignore_errors=True)


def names_file(line: str, name: str) -> bool:
    """Tell whether an output line names a changed file (L-34 d).

    The line holds the whole path, or a path printed from a service or package root: a printed path of at least two
    components that the changed file's path ends with (``tests/api/test_x.py`` names ``services/a/tests/api/test_x.py``).
    """
    if name in line:
        return True
    return any(name.endswith("/" + printed) for printed in PRINTED_PATH.findall(line))


def failing_files(out: str, changed: List[str]) -> List[Tuple[str, str]]:
    """Return the ticket's files a failed check's output names, each with the output lines that name it (L-32).

    A tool reports the file it fails on (``services/missions/tests/api/cli/test_x.py:27:18``), which is rarely the first
    file it was given: the failure goes to the owner of the file named, so that the right task fixes it.
    """
    # A line naming many of the ticket's files is a list (an echoed command, a list of files checked), not a failure.
    lines = [line for line in out.splitlines() if sum(names_file(line, name) for name in changed) <= 2]
    found: List[Tuple[str, str]] = []
    for name in sorted(changed, key=len, reverse=True):
        hits = [line for line in lines if names_file(line, name)]
        if hits and not any(name in other for other, _ in found):
            found.append((name, "\n".join(hits[:12])))
    order = {name: index for index, name in enumerate(changed)}
    return sorted(found, key=lambda pair: order.get(pair[0], 0))[:FAILING_FILES_MAX]


class Checks:
    def __init__(self, ticket: str, root: Path = ROOT, changed: Optional[List[str]] = None) -> None:
        self.root = root
        self.changed = changed or []
        self.evidence = ROOT / "docs" / "tickets" / ticket / "tests-evidences"
        self.evidence.mkdir(parents=True, exist_ok=True)
        self.failures: List[Dict[str, Union[str, bool]]] = []
        self.not_applicable: List[str] = []
        self.passed: List[str] = []

    def check(
        self, name: str, command: List[str], file: str, cwd: Optional[Path] = None, env: Optional[Dict[str, str]] = None
    ) -> bool:
        folder = cwd if cwd else self.root
        code, out = run(command, folder, env)
        slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
        where = "the ticket's own files only" if self.root != ROOT else "the main checkout"
        (self.evidence / f"{slug}.txt").write_text(
            f"$ {' '.join(command)}\n(cwd {folder.relative_to(self.root) or '.'}, on {where})\n\n{out}\n",
            encoding="utf-8",
        )
        if code == 0:
            self.passed.append(name)
            return True
        detail = "\n".join(out.splitlines()[-12:])
        environment = environment_failure(code, out, self.root)
        named = [] if environment else failing_files(out, self.changed)
        if not named:
            self.failures.append({"check": name, "file": file, "detail": detail[:1500], "environment": environment})
            return False
        for path, lines in named:
            self.failures.append(
                {"check": name, "file": path, "detail": f"{lines}\n...\n{detail}"[:1500], "environment": False}
            )
        return False

    def skip(self, name: str, reason: str) -> None:
        self.not_applicable.append(f"{name}: {reason}")


def python_checks(checks: Checks, changed: List[str]) -> None:
    root = checks.root
    files = [f for f in changed if f.endswith(".py") and f.startswith(PROJECT_PREFIXES) and (root / f).exists()]
    if not files:
        checks.skip("python", "no Python project file changed")
        return
    checks.check("ruff check", ["uv", "run", "ruff", "check", *files], files[0])
    checks.check("ruff format", ["uv", "run", "ruff", "format", "--check", *files], files[0])
    install_swarm_core(checks)
    sources = sorted(str(p.relative_to(root)) for pattern in MYPY_SOURCE_GLOBS for p in root.glob(pattern))
    if sources:
        checks.check("mypy", ["uv", "run", "mypy", *sources], sources[0])
    else:
        checks.skip("mypy", f"not run, no source folder in the tree ({', '.join(MYPY_SOURCE_GLOBS)})")
    checks.check("pytest", ["uv", "run", "pytest", "-q", "-n", "2"], "tests")


def rust_checks(checks: Checks, changed: List[str]) -> None:
    manifest = checks.root / "rust" / "Cargo.toml"
    # The clean tree shares the main checkout's build folder, so a check does not rebuild every crate from scratch.
    target = {"CARGO_TARGET_DIR": str(ROOT / "rust" / "target")}
    if not any(f.startswith("rust/") for f in changed) or not manifest.exists():
        checks.skip("rust", "no Rust change")
        return
    checks.check(
        "cargo metadata",
        ["cargo", "metadata", "--no-deps", "--format-version", "1", "--locked", "--manifest-path", str(manifest)],
        "rust/Cargo.toml",
        env=target,
    )
    members = re.search(r"members\s*=\s*\[(.*?)\]", manifest.read_text(encoding="utf-8"), re.DOTALL)
    if not members or not members.group(1).strip():
        for name in ("cargo fmt", "cargo clippy", "cargo test"):
            checks.skip(name, "the Cargo workspace has no member crate yet")
        return
    cwd = manifest.parent
    checks.check("cargo fmt", ["cargo", "fmt", "--all", "--check"], "rust", cwd, target)
    checks.check(
        "cargo clippy",
        ["cargo", "clippy", "--workspace", "--all-targets", "--", "-D", "warnings"],
        "rust",
        cwd,
        target,
    )
    checks.check("cargo test", ["cargo", "test", "--workspace"], "rust", cwd, target)


def typescript_checks(checks: Checks, changed: List[str]) -> None:
    if not any(
        f.startswith(("frontend/apps/", "frontend/packages/"))
        or f in ("package.json", "pnpm-workspace.yaml", "turbo.json")
        for f in changed
    ):
        checks.skip("typescript", "no TypeScript change")
        return
    root = checks.root
    packages = [
        p
        for pattern in ("frontend/apps/*/package.json", "frontend/packages/*/package.json")
        for p in root.glob(pattern)
    ]
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
    tf = [f for f in changed if f.startswith("infra/terraform/") and f.endswith((".tf", ".tftest.hcl"))]
    if not tf:
        checks.skip("terraform", "no Terraform change")
        return
    checks.check("terraform fmt", ["terraform", "fmt", "-check", "-recursive", "infra/terraform"], "infra/terraform")
    folders = sorted({str(Path(f).parent) if not f.endswith(".tftest.hcl") else str(Path(f).parent.parent) for f in tf})
    for folder in folders:
        path = checks.root / folder
        if not list(path.glob("*.tf")):
            continue
        if not checks.check(
            f"terraform init {folder}", ["terraform", "init", "-backend=false", "-input=false"], folder, path
        ):
            continue
        checks.check(f"terraform validate {folder}", ["terraform", "validate"], folder, path)
        if (path / "tests").is_dir():
            checks.check(f"terraform test {folder}", ["terraform", "test"], folder, path)


def main() -> int:
    args = sys.argv[1:]
    ticket = args[args.index("--ticket") + 1] if "--ticket" in args else ""
    base = args[args.index("--base") + 1] if "--base" in args else "develop"
    if not re.fullmatch(r"T\d\.\d\d", ticket):
        print(USAGE, file=sys.stderr)
        return 2
    changed = changed_files(base, ticket)
    tree = isolated_tree(changed) if own_paths(ticket) is not None else ROOT
    try:
        verdict = run_checks(ticket, base, changed, tree)
    except Exception as error:
        print(f"The checks stopped: {type(error).__name__}: {error}", file=sys.stderr)
        raise
    finally:
        if tree != ROOT:
            remove_tree(tree)
    print(json.dumps(verdict))
    return 0 if verdict["passed"] else 1


def run_checks(
    ticket: str, base: str, changed: List[str], root: Path
) -> Dict[str, Union[bool, List[str], List[Dict[str, Union[str, bool]]]]]:
    """Run every applicable check of the ticket in ``root`` and return the verdict."""
    checks = Checks(ticket, root, changed)
    python_checks(checks, changed)
    rust_checks(checks, changed)
    typescript_checks(checks, changed)
    terraform_checks(checks, changed)
    _, develop_files = run(["git", "ls-tree", "-r", "--name-only", base, f"docs/tickets/{PIPELINE_TICKET}"])
    pipeline_ready = ticket == PIPELINE_TICKET or f"docs/tickets/{PIPELINE_TICKET}/EXPLAIN.md" in develop_files
    screen_failures, screen_reason = screen_problems(root, ticket, changed, pipeline_ready)
    if screen_reason:
        checks.skip("screens captured", screen_reason)
    elif screen_failures:
        for file, detail in screen_failures:
            checks.failures.append({"check": "screens captured", "file": file, "detail": detail, "environment": False})
    else:
        checks.passed.append("screens captured")
    checks.check("specs check", ["python3", ".claude/skills/write-specs/scripts/specs.py", "check"], "docs/specs")
    folder = f"docs/tickets/{ticket}"
    checks.check(
        "ticket refs", ["python3", ".claude/scripts/tickets/ticket_refs.py", "check", "--ticket", ticket], folder
    )
    if (root / folder / "PLAN.md").is_file():
        checks.check(
            "plan view",
            ["python3", ".claude/scripts/tickets/plan.py", "check", "--ticket", ticket],
            f"{folder}/PLAN.md",
        )
    return {
        "passed": not checks.failures,
        "failures": checks.failures,
        "not_applicable": checks.not_applicable,
        "passed_checks": checks.passed,
    }


if __name__ == "__main__":
    sys.exit(main())
