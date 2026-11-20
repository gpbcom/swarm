from __future__ import annotations

import shutil
from pathlib import Path
from typing import ClassVar, Dict, List

import pytest

from tests.ci.detect_changes.helpers import ALL_SERVICES, ALL_TYPESCRIPT, RUST_KEY, outputs, run_detector, write_repo


class TestSharedChanges:
    EVERYTHING: ClassVar[Dict[str, str]] = {
        "services": ALL_SERVICES,
        "typescript": ALL_TYPESCRIPT,
        "rust": "true",
        "repository": "true",
        "specs": "true",
    }

    @pytest.mark.parametrize(
        "path",
        [
            "packages/python/lifecycle/src/lifecycle/runnable.py",
            "packages/ts/config/eslint.config.js",
            "packages/rust/core/src/lib.rs",
            "packages/rust/Cargo.lock",
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
        result = run_detector(tmp_path, ["packages/rust/Cargo.toml"])
        assert outputs(result) == {**self.EVERYTHING, RUST_KEY: "false"}

    def test_a_shared_path_with_a_service_path_lists_each_service_once(self, tmp_path: Path) -> None:
        write_repo(tmp_path)
        changed: List[str] = ["uv.lock", "services/alpha/src/alpha/main.py"]
        result = run_detector(tmp_path, changed)
        assert outputs(result)["services"] == ALL_SERVICES

    def test_a_repository_without_services_gives_an_empty_list(self, tmp_path: Path) -> None:
        write_repo(tmp_path)
        shutil.rmtree(tmp_path / "services")
        result = run_detector(tmp_path, ["uv.lock"])
        assert outputs(result)["services"] == "[]"

    def test_the_terraform_workflow_selects_nothing(self, tmp_path: Path) -> None:
        write_repo(tmp_path)
        result = run_detector(tmp_path, [".github/workflows/terraform.yml"])
        values = outputs(result)
        assert values["services"] == "[]"
        assert values["typescript"] == "[]"
        assert values["rust"] == "false"
