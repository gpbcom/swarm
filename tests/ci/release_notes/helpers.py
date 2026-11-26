from __future__ import annotations

# Standard library imports
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict

GIT_ENV: Dict[str, str] = {
    "GIT_AUTHOR_NAME": "Test",
    "GIT_AUTHOR_EMAIL": "test@example.com",
    "GIT_COMMITTER_NAME": "Test",
    "GIT_COMMITTER_EMAIL": "test@example.com",
}
TICKET = "T9.01"
TICKET_TITLE = "Mission catalogue"
FEATURE = "📘 FS-012: Plan a Mission"
RULE = "📏 BR-008: Operator isolation"
JUNIT = (
    '<?xml version="1.0" encoding="utf-8"?><testsuites><testsuite name="pytest" errors="{errors}" failures="0" '
    'skipped="1" tests="10" time="2.5"></testsuite></testsuites>'
)
RUST_LOG = (
    "test result: ok. 7 passed; 0 failed; 2 ignored; 0 measured\ntest result: ok. 3 passed; 0 failed; 0 ignored\n"
)
VITEST_LOG = " Test Files  2 passed (2)\n      Tests  12 passed (12)\n"
NODE_TEST_LOG = "ok 1 - generated models\n1..1\n# tests 9\n# suites 1\n# pass 8\n# fail 0\n# skipped 1\n# todo 0\n"


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def git(cwd: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=cwd, check=True, capture_output=True, text=True, env={**os.environ, **GIT_ENV}
    )
    return result.stdout.strip()


def run(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    script = repo_root() / ".github" / "scripts" / "release_notes.py"
    return subprocess.run(
        [sys.executable, str(script), "--root", str(root), *args], capture_output=True, text=True, check=False
    )


def merge_branch(root: Path, branch: str, subjects: Dict[str, str], merge_subject: str) -> None:
    """Merge into develop, with a merge commit, a branch holding one commit per file of ``subjects``."""
    git(root, "checkout", "-q", "-b", branch, "develop")
    for name, subject in subjects.items():
        (root / name).parent.mkdir(parents=True, exist_ok=True)
        (root / name).write_text(subject + "\n", encoding="utf-8")
        git(root, "add", name)
        git(root, "commit", "-q", "-m", subject)
    git(root, "checkout", "-q", "develop")
    git(root, "merge", "-q", "--no-ff", branch, "-m", merge_subject)


def make_repo(base: Path) -> Path:
    """A repository on develop, released once (tag v0.1.0), then a ticket and a harness change merged."""
    root = base / "repo"
    root.mkdir()
    git(root, "init", "-q", "-b", "develop")
    git(root, "commit", "-q", "--allow-empty", "-m", "Initial commit")
    merge_branch(
        root, "feature/old", {"old.txt": "Harness: an old change"}, "Harness: merge feature/old into develop (#1)"
    )
    git(root, "tag", "v0.1.0")
    ticket_files = {
        f"docs/tickets/{TICKET}/TICKET.md": f"{TICKET}: tests first",
        f"docs/tickets/{TICKET}/EXPLAIN.md": f"{TICKET}: {TICKET_TITLE}",
    }
    merge_branch(root, "feature/tickets", ticket_files, f"{TICKET}: merge feature/tickets into develop (#7)")
    (root / "docs" / "tickets" / TICKET / "TICKET.md").write_text(
        f"# {TICKET}: {TICKET_TITLE}\n\n- [{FEATURE}](../../specs/functional/features/FS-012.md)\n"
        f"- [{RULE}](../../specs/functional/business-rules/BR-008.md)\n",
        encoding="utf-8",
    )
    git(root, "commit", "-q", "-am", f"{TICKET}: {TICKET_TITLE}")
    merge_branch(
        root,
        "feature/harness-x",
        {"x.py": "Harness: every branch gets a verdict"},
        "Harness: merge feature/harness-x into develop (#8)",
    )
    return root


def write_reports(base: Path, errors: int = 0) -> Path:
    """Write the reports CI uploads: one folder per artifact."""
    reports = base / "reports"
    for folder, name, text in (
        ("test-report-python-repository", "repository.xml", JUNIT.format(errors=errors)),
        ("test-report-rust", "rust-cargo-test.log", RUST_LOG),
        ("test-report-ts-frontend-apps-ground-control", "typescript.log", VITEST_LOG),
        ("test-report-specs", "specs-check.log", ""),
        ("test-report-ts-packages-ts-live", "packages-ts-live.log", NODE_TEST_LOG),
        ("test-report-ts-packages-ts-config", "packages-ts-config.log", ""),
    ):
        (reports / folder).mkdir(parents=True)
        (reports / folder / name).write_text(text, encoding="utf-8")
    return reports
