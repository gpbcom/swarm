from __future__ import annotations

# Standard library imports
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List

# Third-party imports
import pytest

ROOT = Path(__file__).resolve().parents[3]
GIT_ENV = {
    "GIT_AUTHOR_NAME": "T",
    "GIT_AUTHOR_EMAIL": "t@example.com",
    "GIT_COMMITTER_NAME": "T",
    "GIT_COMMITTER_EMAIL": "t@example.com",
}
TICKET = "T9.01"


def git(cwd: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, env={**os.environ, **GIT_ENV})


def changed(repo: Path) -> List[str]:
    code = (
        f"import sys; sys.path.insert(0, {str(ROOT / '.claude' / 'scripts' / 'tickets')!r}); import checks; "
        f"print('\\n'.join(checks.changed_files('develop', {TICKET!r}, __import__('pathlib').Path({str(repo)!r}))))"
    )
    result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, check=True)
    return [line for line in result.stdout.splitlines() if line]


FRONT_END = "T0.16"
SCREEN_ROW = '| <a id="screen-a1"></a>A1: Enter the Operator | ➖ | ➖ | {source} | screens |'


def screen_verdict(root: Path, changed: List[str], pipeline_ready: bool) -> Dict[str, object]:
    code = (
        f"import sys, json; sys.path.insert(0, {str(ROOT / '.claude' / 'scripts' / 'tickets')!r}); import checks; "
        f"from pathlib import Path; failures, reason = checks.screen_problems(Path({str(root)!r}), {FRONT_END!r}, "
        f"{changed!r}, {pipeline_ready!r}); print(json.dumps({{'failures': failures, 'reason': reason}}))"
    )
    result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, check=True)
    loaded: Dict[str, object] = json.loads(result.stdout)
    return loaded


def front_end_ticket(
    root: Path, source: str, screens: str = "- [🖼️ UC-029 A1](../../specs/screens/UC-029/a1.png)", mockup: bool = True
) -> Path:
    for folder in (
        "docs/specs/roadmap/gantt",
        "docs/specs/functional/use-cases",
        f"docs/tickets/{FRONT_END}",
        "docs/specs/screens/UC-029",
        "docs/specs/screens/mockups/UC-029",
    ):
        (root / folder).mkdir(parents=True, exist_ok=True)
    graph = {"tickets": {FRONT_END: {"deps": [], "external": [], "area": "frontend/apps/back-office", "size": "M"}}}
    (root / "docs/specs/roadmap/gantt/ticket-graph.json").write_text(json.dumps(graph), encoding="utf-8")
    (root / "docs/specs/functional/use-cases/UC-029-create-an-operator.md").write_text(
        f"# UC-029\n\n{SCREEN_ROW.format(source=source)}\n", encoding="utf-8"
    )
    (root / f"docs/tickets/{FRONT_END}/TICKET.md").write_text(
        f"# {FRONT_END}: Create an Operator\n\n## Screens touched\n\n{screens}\n\n## Budgets touched\n",
        encoding="utf-8",
    )
    for name in ("a1.png", "a1.dark.png"):
        (root / "docs/specs/screens/UC-029" / name).write_bytes(b"png")
    if mockup:
        (root / "docs/specs/screens/mockups/UC-029/a1.html").write_text("<html></html>", encoding="utf-8")
    return root


CAPTURED = ["docs/specs/screens/UC-029/a1.png", "docs/specs/screens/UC-029/a1.dark.png"]


def two_tickets_at_work(tmp_path: Path, paths: object) -> Path:
    git(tmp_path, "init", "-b", "develop")
    (tmp_path / "base.txt").write_text("base\n", encoding="utf-8")
    git(tmp_path, "add", "-A")
    git(tmp_path, "commit", "-m", "base")
    for name in ("services/mine/a.py", "services/theirs/b.py", f"docs/tickets/{TICKET}/TICKET.md"):
        (tmp_path / name).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / name).write_text("x = 1\n", encoding="utf-8")
    state = tmp_path / ".git" / "swarm" / TICKET
    state.mkdir(parents=True)
    (state / "state.json").write_text(json.dumps({"ticket": TICKET, "paths": paths}), encoding="utf-8")
    return tmp_path


def clean_tree(repo: Path) -> Dict[str, object]:
    code = (
        f"import sys, json; sys.path.insert(0, {str(ROOT / '.claude' / 'scripts' / 'tickets')!r}); import checks; "
        f"from pathlib import Path; repo = Path({str(repo)!r}); "
        f"tree = checks.isolated_tree(checks.changed_files('develop', {TICKET!r}, repo), repo); "
        f"files = sorted(str(p.relative_to(tree)) for p in tree.rglob('*') if p.is_file() and '.git' not in p.parts); "
        f"texts = {{name: (tree / name).read_text() for name in files}}; "
        f"checks.remove_tree(tree, repo); "
        f"print(json.dumps({{'files': files, 'texts': texts, 'gone': not tree.exists()}}))"
    )
    result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, check=True)
    loaded: Dict[str, object] = json.loads(result.stdout)
    return loaded


class TestChecks:
    def test_a_ticket_is_checked_on_its_own_files_only(self, tmp_path: Path) -> None:
        repo = two_tickets_at_work(tmp_path, ["services/mine/a.py", f"docs/tickets/{TICKET}/"])
        assert changed(repo) == [f"docs/tickets/{TICKET}/TICKET.md", "services/mine/a.py"]

    def test_a_ticket_without_recorded_files_is_checked_on_every_change(self, tmp_path: Path) -> None:
        repo = two_tickets_at_work(tmp_path, None)
        assert "services/theirs/b.py" in changed(repo)

    def test_screens_are_not_checked_before_the_screenshot_pipeline_exists(self, tmp_path: Path) -> None:
        verdict = screen_verdict(front_end_ticket(tmp_path, "✏️ Mock-up"), [], False)
        assert verdict["failures"] == []
        assert "T0.20" in str(verdict["reason"])

    def test_a_screen_still_drawn_as_a_mock_up_fails_the_ticket(self, tmp_path: Path) -> None:
        verdict = screen_verdict(front_end_ticket(tmp_path, "✏️ Mock-up"), [], True)
        failures = verdict["failures"]
        assert isinstance(failures, list)
        assert any("UC-029 a1" in str(failure) for failure in failures)
        assert any("docs/specs/screens/UC-029/a1.png" == failure[0] for failure in failures)

    def test_a_screen_captured_by_the_ticket_passes(self, tmp_path: Path) -> None:
        root = front_end_ticket(tmp_path, "📸 Screenshot", mockup=False)
        verdict = screen_verdict(root, CAPTURED, True)
        assert verdict == {"failures": [], "reason": None}

    def test_a_screenshot_must_be_taken_by_the_ticket_itself(self, tmp_path: Path) -> None:
        root = front_end_ticket(tmp_path, "📸 Screenshot", mockup=False)
        failures = screen_verdict(root, CAPTURED[:1], True)["failures"]
        assert isinstance(failures, list)
        assert [failure[0] for failure in failures] == ["docs/specs/screens/UC-029/a1.dark.png"]

    def test_a_ticket_that_shows_no_screen_says_why_and_is_not_checked(self, tmp_path: Path) -> None:
        root = front_end_ticket(
            tmp_path, "✏️ Mock-up", screens="- ➖ No screen: the shells hold no state of a use case yet."
        )
        verdict = screen_verdict(root, [], True)
        assert verdict["failures"] == []
        assert "No screen" in str(verdict["reason"])

    def test_the_checks_run_on_a_clean_tree_of_the_ticket_s_own_work_only(self, tmp_path: Path) -> None:
        repo = two_tickets_at_work(tmp_path, ["services/mine/", "base.txt", "gone.txt", f"docs/tickets/{TICKET}/"])
        (repo / "gone.txt").write_text("old\n", encoding="utf-8")
        (repo / "shared.txt").write_text("committed\n", encoding="utf-8")
        git(repo, "add", "gone.txt", "shared.txt")
        git(repo, "commit", "-m", "two more files")
        (repo / "gone.txt").unlink()
        (repo / "base.txt").write_text("changed by the ticket\n", encoding="utf-8")
        (repo / "shared.txt").write_text("changed by another ticket\n", encoding="utf-8")
        verdict = clean_tree(repo)
        assert verdict["files"] == [
            "base.txt",
            f"docs/tickets/{TICKET}/TICKET.md",
            "services/mine/a.py",
            "shared.txt",
        ]
        texts = verdict["texts"]
        assert isinstance(texts, dict)
        assert texts["base.txt"] == "changed by the ticket\n"
        assert texts["shared.txt"] == "committed\n"
        assert verdict["gone"] is True
        listed = subprocess.run(["git", "worktree", "list"], cwd=repo, capture_output=True, text=True, check=True)
        assert len(listed.stdout.splitlines()) == 1

    @pytest.mark.parametrize(
        ("code", "out", "environment"),
        [
            (127, "command not found: cargo", True),
            (1, "ModuleNotFoundError: No module named 'asyncpg'", True),
            (1, "ModuleNotFoundError: No module named 'tests.api'", False),
            (1, "ModuleNotFoundError: No module named 'swarm_rest.api'", False),
            (1, "ModuleNotFoundError: No module named 'asyncpg'\nNo module named 'tests.api'", False),
            (1, "AssertionError: 1 != 2", False),
        ],
    )
    def test_a_missing_module_of_the_project_is_the_code_s_fault_not_the_environment_s(
        self, tmp_path: Path, code: int, out: str, environment: bool
    ) -> None:
        (tmp_path / "tests").mkdir()
        (tmp_path / "packages/python/swarm-rest/src/swarm_rest").mkdir(parents=True)
        script = (
            f"import sys; sys.path.insert(0, {str(ROOT / '.claude' / 'scripts' / 'tickets')!r}); import checks; "
            f"from pathlib import Path; print(checks.environment_failure({code!r}, {out!r}, Path({str(tmp_path)!r})))"
        )
        result = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True, check=True)
        assert result.stdout.strip() == str(environment)

    def test_a_failure_goes_to_the_file_the_tool_names_not_to_the_first_file_it_was_given(self) -> None:
        changed = [
            "packages/python/swarm-rest/src/swarm_rest/__init__.py",
            "services/missions/tests/api/cli/test_missions_console_scripts.py",
            "services/fleet/tests/api/cli/test_fleet_console_scripts.py",
        ]
        out = (
            f"$ uv run ruff check {' '.join(changed)}\n"
            "PLW1510 `subprocess.run` without explicit `check` argument\n"
            "  --> services/missions/tests/api/cli/test_missions_console_scripts.py:27:18\n"
            "PLW1510 `subprocess.run` without explicit `check` argument\n"
            "  --> /tmp/swarm-checks-x/services/fleet/tests/api/cli/test_fleet_console_scripts.py:27:18\n"
            "Found 2 errors.\n"
        )
        script = (
            f"import sys, json; sys.path.insert(0, {str(ROOT / '.claude' / 'scripts' / 'tickets')!r}); import checks; "
            f"print(json.dumps(checks.failing_files({out!r}, {changed!r})))"
        )
        result = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True, check=True)
        named = json.loads(result.stdout)
        assert [path for path, _ in named] == changed[1:]
        assert ":27:18" in named[0][1]
