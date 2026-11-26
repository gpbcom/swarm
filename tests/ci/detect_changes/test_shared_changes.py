from __future__ import annotations

# Standard library imports
import shutil
from pathlib import Path
from typing import ClassVar, Dict, List

# Third-party imports
import pytest

# First-party imports
from tests.ci.detect_changes.helpers import (
    ALL_IMAGES,
    ALL_SERVICES,
    ALL_TYPESCRIPT,
    IMAGES_KEY,
    RUST_KEY,
    outputs,
    run_detector,
    write_repo,
)


class TestSharedChanges:
    EVERYTHING: ClassVar[Dict[str, str]] = {
        "services": ALL_SERVICES,
        "typescript": ALL_TYPESCRIPT,
        "rust": "true",
        "repository": "true",
        "specs": "true",
        "images": ALL_IMAGES,
    }

    @pytest.mark.parametrize(
        "path",
        [
            "backend/libs/swarm-lifecycle/src/swarm_lifecycle/runnables/runnable.py",
            "frontend/packages/config/eslint.config.js",
            "qa/e2e/playwright.config.ts",
            "scripts/src/swarm_scripts/openapi/export.py",
            "rust/core/src/lib.rs",
            "rust/Cargo.lock",
            "uv.lock",
            "pnpm-lock.yaml",
            "pyproject.toml",
            "package.json",
            "pnpm-workspace.yaml",
            "turbo.json",
            ".github/workflows/ci.yml",
            ".github/workflows/python.yml",
            ".github/workflows/rust.yml",
            ".github/workflows/typescript.yml",
            ".github/workflows/specs.yml",
            ".github/scripts/detect_changes.py",
            ".github/workflows/images.yml",
            "infra/compose/e2e.yaml",
            ".dockerignore",
        ],
    )
    def test_a_shared_path_alone_runs_everything(self, tmp_path: Path, path: str) -> None:
        write_repo(tmp_path)
        result = run_detector(tmp_path, [path])
        assert result.returncode == 0
        assert outputs(result) == self.EVERYTHING

    def test_all_runs_everything_with_empty_stdin(self, tmp_path: Path) -> None:
        write_repo(tmp_path)
        result = run_detector(tmp_path, [], "--all")
        assert result.returncode == 0
        assert outputs(result) == self.EVERYTHING

    def test_an_empty_rust_workspace_is_not_applicable(self, tmp_path: Path) -> None:
        write_repo(tmp_path, rust_members=False)
        result = run_detector(tmp_path, ["rust/Cargo.toml"])
        assert outputs(result) == {**self.EVERYTHING, RUST_KEY: "false"}

    def test_a_shared_path_with_an_app_path_lists_each_app_once(self, tmp_path: Path) -> None:
        write_repo(tmp_path)
        changed: List[str] = ["uv.lock", "backend/apps/alpha/src/swarm_alpha/main.py"]
        result = run_detector(tmp_path, changed)
        assert outputs(result)["services"] == ALL_SERVICES

    def test_a_repository_without_apps_gives_an_empty_list(self, tmp_path: Path) -> None:
        write_repo(tmp_path)
        shutil.rmtree(tmp_path / "backend" / "apps")
        result = run_detector(tmp_path, ["uv.lock"])
        assert outputs(result)["services"] == "[]"

    def test_the_terraform_workflow_selects_nothing(self, tmp_path: Path) -> None:
        write_repo(tmp_path)
        result = run_detector(tmp_path, [".github/workflows/terraform.yml"])
        values = outputs(result)
        assert values["services"] == "[]"
        assert values["typescript"] == "[]"
        assert values["rust"] == "false"
        assert values[IMAGES_KEY] == "[]"
