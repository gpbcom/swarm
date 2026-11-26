from __future__ import annotations

# Standard library imports
from pathlib import Path
from typing import List

# Third-party imports
import pytest

# First-party imports
from tests.harness.check_touched.helpers import add_worktree, make_repo, repo_root, run_hook

CATALOGUE_RELATIVE = ".claude/hooks/layer-checks.json"


class TestCheckTouchedLayout:
    def dry_run(self, tmp_path: Path, created: List[str], present: List[str]) -> List[str]:
        catalogue = (repo_root() / CATALOGUE_RELATIVE).read_text(encoding="utf-8")
        tmp_path.mkdir(parents=True, exist_ok=True)
        main = make_repo(tmp_path, catalogue)
        worker = add_worktree(main, tmp_path)
        for relative in created:
            path = worker / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("x = 1\n", encoding="utf-8")
        for relative in present:
            (worker / relative).mkdir(parents=True, exist_ok=True)
        return run_hook(worker, "--dry-run").stdout.splitlines()

    def test_a_layer_package_change_lists_ruff_mypy_and_the_tests_that_mirror_it(self, tmp_path: Path) -> None:
        source = "backend/swarm-service/src/swarm_service/drones/x/y.py"
        before = self.dry_run(tmp_path / "a", [source], [])
        assert any(line.endswith(f"uv run ruff check {source}") for line in before)
        assert any(line.endswith(f"uv run ruff format --check {source}") for line in before)
        assert any(line.endswith("uv run mypy backend/swarm-service/src") for line in before)
        assert not any("pytest" in line for line in before)
        after = self.dry_run(tmp_path / "b", [source], ["tests/swarm_service/drones/x"])
        assert any(line.endswith("uv run pytest tests/swarm_service/drones/x -n 2") for line in after)

    def test_a_change_only_under_tests_lists_ruff_but_no_pytest(self, tmp_path: Path) -> None:
        test_file = "tests/swarm_service/drones/x/test_y.py"
        lines = self.dry_run(tmp_path, [test_file], [])
        assert any(line.endswith(f"uv run ruff check {test_file}") for line in lines)
        assert not any("pytest" in line for line in lines)

    def test_an_app_change_lists_its_mypy_check(self, tmp_path: Path) -> None:
        lines = self.dry_run(tmp_path, ["backend/apps/gateway/src/gateway/main.py"], [])
        assert any(line.endswith("uv run mypy backend/apps/gateway/src") for line in lines)

    def test_a_script_is_linted(self, tmp_path: Path) -> None:
        lines = self.dry_run(tmp_path, ["scripts/tool.py"], [])
        assert any(line.endswith("uv run ruff check scripts/tool.py") for line in lines)

    def test_a_script_change_lists_mypy_and_the_tests_that_mirror_it(self, tmp_path: Path) -> None:
        source = "scripts/src/swarm_scripts/openapi/export.py"
        before = self.dry_run(tmp_path / "a", [source], [])
        assert any(line.endswith("uv run mypy scripts/src") for line in before)
        assert not any("pytest" in line for line in before)
        after = self.dry_run(tmp_path / "b", [source], ["tests/scripts/openapi"])
        assert any(line.endswith("uv run pytest tests/scripts/openapi -n 2") for line in after)

    @pytest.mark.parametrize("name", ["cargo fmt", "cargo clippy", "cargo test"])
    def test_a_rust_change_lists_its_cargo_checks_when_the_crate_exists(self, tmp_path: Path, name: str) -> None:
        lines = self.dry_run(tmp_path, ["rust/core/src/lib.rs"], [])
        assert not any("cargo" in line for line in lines)
        with_manifest = self.dry_run(tmp_path / "m", ["rust/core/src/lib.rs", "rust/core/Cargo.toml"], [])
        assert any(name in line and "rust/core/Cargo.toml" in line for line in with_manifest)

    @pytest.mark.parametrize("parent", ["frontend/apps", "frontend/packages"])
    def test_a_front_end_change_lists_its_pnpm_checks(self, tmp_path: Path, parent: str) -> None:
        lines = self.dry_run(tmp_path, [f"{parent}/ui/src/a.ts", f"{parent}/ui/package.json"], [])
        assert any(line.endswith(f"pnpm --filter ./{parent}/ui run --if-present lint") for line in lines)

    def test_an_infra_change_lists_the_terraform_format_check(self, tmp_path: Path) -> None:
        lines = self.dry_run(tmp_path, ["infra/terraform/cells/dev/main.tf"], [])
        assert any("terraform fmt -check -recursive infra/terraform/cells/dev" in line for line in lines)
