from __future__ import annotations

import json
from pathlib import Path

from tests.harness.tickets.helpers import (
    DONE,
    FIELD,
    NEXT,
    OTHER_AREA,
    SAME_AREA,
    git,
    lines,
    make_repo,
    open_ticket,
    run,
)


class TestTickets:
    def test_a_ticket_whose_prerequisites_are_merged_may_start(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        result = run(main, "check", "--ticket", NEXT)
        assert result.returncode == 0, result.stdout
        assert result.stdout == ""

    def test_a_ticket_with_an_open_prerequisite_waits(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        result = run(main, "check", "--ticket", OTHER_AREA)
        assert result.returncode == 1
        assert NEXT in result.stdout
        assert "not merged" in result.stdout

    def test_a_ticket_waits_while_an_open_ticket_changes_the_same_area(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        open_ticket(main, NEXT)
        result = run(main, "check", "--ticket", SAME_AREA)
        assert result.returncode == 1
        assert "services/missions" in result.stdout
        assert NEXT in result.stdout

    def test_a_ticket_does_not_wait_for_its_own_worktree(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        open_ticket(main, NEXT)
        assert run(main, "check", "--ticket", NEXT).returncode == 0

    def test_a_field_ticket_waits_for_its_campaign(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        result = run(main, "check", "--ticket", FIELD)
        assert result.returncode == 1
        assert "C-01" in result.stdout

    def test_force_reports_the_problems_but_lets_the_ticket_start(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        result = run(main, "check", "--ticket", OTHER_AREA, "--force")
        assert result.returncode == 0
        assert NEXT in result.stdout

    def test_list_shows_every_open_ticket(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        open_ticket(main, NEXT)
        open_ticket(main, OTHER_AREA)
        shown = "\n".join(lines(run(main, "list")))
        assert NEXT in shown
        assert OTHER_AREA in shown
        assert DONE not in shown

    def test_the_workspace_holds_develop_and_every_open_ticket(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        home = open_ticket(main, NEXT)
        assert run(main, "workspace").returncode == 0
        workspace = json.loads((main / "swarm.code-workspace").read_text(encoding="utf-8"))
        paths = [folder["path"] for folder in workspace["folders"]]
        assert paths[0] == "."
        assert str(home) in paths
        assert "GitHub.vscode-pull-request-github" in workspace["extensions"]["recommendations"]

    def test_prune_removes_the_worktree_of_a_merged_ticket(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        home = open_ticket(main, NEXT)
        (home / "docs" / "tickets" / NEXT).mkdir(parents=True)
        (home / "docs" / "tickets" / NEXT / "EXPLAIN.md").write_text("# Explain\n", encoding="utf-8")
        git(home, "add", "-A")
        git(home, "commit", "-m", f"{NEXT}: work")
        git(main, "merge", "--no-ff", f"feature/{NEXT}", "-m", "merge")
        result = run(main, "prune")
        assert result.returncode == 0, result.stderr
        assert not home.exists()
        assert "feature/" + NEXT not in git(main, "branch", "--list")

    def test_prune_keeps_the_worktree_of_a_ticket_still_running(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        home = open_ticket(main, NEXT)
        assert run(main, "prune").returncode == 0
        assert home.exists()

    def test_setup_turns_on_the_gitflow_hooks(self, tmp_path: Path) -> None:
        main = make_repo(tmp_path)
        assert run(main, "setup").returncode == 0
        assert git(main, "config", "core.hooksPath") == ".githooks"
