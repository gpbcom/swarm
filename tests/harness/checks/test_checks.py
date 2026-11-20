from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List

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
        f"import sys; sys.path.insert(0, {str(ROOT / '.claude' / 'scripts')!r}); import checks; "
        f"print('\\n'.join(checks.changed_files('develop', {TICKET!r}, __import__('pathlib').Path({str(repo)!r}))))"
    )
    result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, check=True)
    return [line for line in result.stdout.splitlines() if line]


FRONT_END = "T0.16"
SCREEN_ROW = '| <a id="screen-a1"></a>A1: Enter the Operator | ➖ | ➖ | {source} | screens |'


def screen_verdict(root: Path, changed: List[str], pipeline_ready: bool) -> Dict[str, object]:
    code = (
        f"import sys, json; sys.path.insert(0, {str(ROOT / '.claude' / 'scripts')!r}); import checks; "
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
    graph = {"tickets": {FRONT_END: {"deps": [], "external": [], "area": "frontends/back-office", "size": "M"}}}
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
