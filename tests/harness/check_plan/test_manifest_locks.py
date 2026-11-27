from __future__ import annotations

# Standard library imports
from pathlib import Path
from typing import List, Tuple

# Third-party imports
import pytest

# First-party imports
from tests.harness.check_plan.helpers import (
    AWAITING,
    FILES_KEY,
    TICKET_ID,
    repo_root,
    run_script,
    with_change,
    write_plan,
)

LOCK_FILES = ("pnpm-lock.yaml", "uv.lock", "rust/Cargo.lock", "frontend/apps/desktop/src-tauri/Cargo.lock")


class TestManifestLocks:
    def run_on(self, tmp_path: Path, files: List[str]) -> Tuple[int, str]:
        write_plan(tmp_path, AWAITING, with_change(3, FILES_KEY, files))
        result = run_script(TICKET_ID, "--root", str(tmp_path))
        return result.returncode, result.stdout

    @pytest.mark.parametrize(
        ("manifest", "lock"),
        [
            pytest.param("frontend/apps/back-office/package.json", "pnpm-lock.yaml", id="front-end-app"),
            pytest.param("frontend/packages/i18n/package.json", "pnpm-lock.yaml", id="front-end-package"),
            pytest.param("qa/e2e/package.json", "pnpm-lock.yaml", id="qa"),
            pytest.param("package.json", "pnpm-lock.yaml", id="root-package-json"),
            pytest.param("backend/libs/swarm-web/pyproject.toml", "uv.lock", id="kernel-library"),
            pytest.param("scripts/pyproject.toml", "uv.lock", id="scripts"),
            pytest.param("pyproject.toml", "uv.lock", id="root-pyproject"),
            pytest.param("rust/swarm-core/safety/Cargo.toml", "rust/Cargo.lock", id="rust-crate"),
            pytest.param(
                "frontend/apps/desktop/src-tauri/Cargo.toml",
                "frontend/apps/desktop/src-tauri/Cargo.lock",
                id="desktop-shell",
            ),
        ],
    )
    def test_a_task_that_changes_a_manifest_without_its_lock_file_is_refused(
        self, tmp_path: Path, manifest: str, lock: str
    ) -> None:
        code, out = self.run_on(tmp_path, [manifest])
        assert code == 1
        assert "task K04" in out
        assert repr(lock) in out

    def test_a_task_that_owns_the_manifest_and_its_lock_file_passes(self, tmp_path: Path) -> None:
        files = ["frontend/apps/back-office/package.json", "pnpm-lock.yaml", "backend/apps/fleet/pyproject.toml"]
        assert self.run_on(tmp_path, [*files, "uv.lock"]) == (0, "")

    @pytest.mark.parametrize(
        "path",
        [
            pytest.param("rust/swarm-core/python/pyproject.toml", id="bindings-outside-the-uv-workspace"),
            pytest.param("infra/charts/cell/Chart.yaml", id="not-a-manifest"),
            pytest.param("docs/package.json", id="outside-the-pnpm-workspace"),
        ],
    )
    def test_a_file_outside_the_workspaces_needs_no_lock_file(self, tmp_path: Path, path: str) -> None:
        assert self.run_on(tmp_path, [path]) == (0, "")

    @pytest.mark.parametrize("lock", LOCK_FILES)
    def test_every_lock_file_is_a_shared_file_of_the_start_rule(self, lock: str) -> None:
        check_plan = (repo_root() / ".claude/skills/ticket/scripts/check_plan.py").read_text(encoding="utf-8")
        tickets = (repo_root() / ".claude/scripts/tickets/tickets.py").read_text(encoding="utf-8")
        assert f'"{lock}"' in check_plan
        assert f'    "{lock}",' in tickets.split("SHARED_FILES = (", 1)[1].split("\n)", 1)[0]
