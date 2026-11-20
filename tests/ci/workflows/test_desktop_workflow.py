from __future__ import annotations

from pathlib import Path
from typing import ClassVar, Dict, List, Union

import pytest
import yaml
from pydantic import JsonValue


class TestDesktopWorkflow:
    READ_ONLY_PERMISSIONS: ClassVar[Dict[str, str]] = {"contents": "read"}
    SHELL: ClassVar[str] = "frontends/desktop/src-tauri"
    PULL_REQUEST_BRANCHES: ClassVar[List[str]] = ["develop", "master", "release/**"]
    PUSH_BRANCHES: ClassVar[List[str]] = ["master", "develop", "release/**", "hotfix/**"]
    PATHS: ClassVar[List[str]] = [
        "frontends/desktop/**",
        "frontends/ground-control/**",
        "frontends/mission-studio/**",
        "packages/ts/**",
        "pnpm-lock.yaml",
        ".github/workflows/desktop.yml",
    ]
    PLATFORMS: ClassVar[List[str]] = ["ubuntu-latest", "windows-latest", "macos-latest"]

    def workflow(self) -> Dict[Union[str, bool], JsonValue]:
        root = Path(__file__).resolve().parents[3]
        text = (root / ".github" / "workflows" / "desktop.yml").read_text(encoding="utf-8")
        data = yaml.safe_load(text)
        assert isinstance(data, dict)
        return data

    def trigger(self) -> Dict[str, JsonValue]:
        data = self.workflow()
        trigger = data.get("on", data.get(True))
        assert isinstance(trigger, dict)
        return trigger

    def build_job(self) -> Dict[str, JsonValue]:
        jobs = self.workflow()["jobs"]
        assert isinstance(jobs, dict)
        assert list(jobs.keys()) == ["build"]
        job = jobs["build"]
        assert isinstance(job, dict)
        return job

    def steps(self) -> List[Dict[str, JsonValue]]:
        steps = self.build_job()["steps"]
        assert isinstance(steps, list)
        return steps

    def runs(self) -> List[str]:
        return [str(step["run"]) for step in self.steps() if "run" in step]

    def steps_running(self, needle: str) -> List[Dict[str, JsonValue]]:
        return [step for step in self.steps() if needle in str(step.get("run", ""))]

    def test_the_name_is_desktop(self) -> None:
        assert self.workflow()["name"] == "desktop"

    @pytest.mark.parametrize(("event", "branches"), [("pull_request", PULL_REQUEST_BRANCHES), ("push", PUSH_BRANCHES)])
    def test_the_triggers_have_their_branches_and_paths(self, event: str, branches: List[str]) -> None:
        trigger = self.trigger()[event]
        assert isinstance(trigger, dict)
        assert trigger["branches"] == branches
        assert trigger["paths"] == self.PATHS

    def test_permissions_are_read_only(self) -> None:
        assert self.workflow()["permissions"] == self.READ_ONLY_PERMISSIONS

    def test_the_matrix_builds_on_three_platforms_without_failing_fast(self) -> None:
        strategy = self.build_job()["strategy"]
        assert isinstance(strategy, dict)
        assert strategy["fail-fast"] is False
        assert strategy["matrix"]["os"] == self.PLATFORMS

    def test_the_job_runs_on_the_matrix_platform(self) -> None:
        assert self.build_job()["runs-on"] == "${{ matrix.os }}"

    def test_the_setup_steps_come_first_in_order(self) -> None:
        uses = [str(step.get("uses", "")) for step in self.steps()[:3]]
        prefixes = ["actions/checkout@", "pnpm/action-setup@", "actions/setup-node@"]
        for used, prefix in zip(uses, prefixes):
            assert used.startswith(prefix)

    def test_node_22_is_set_up_with_the_pnpm_cache(self) -> None:
        options = self.steps()[2]["with"]
        assert isinstance(options, dict)
        assert str(options["node-version"]).startswith("22")
        assert options["cache"] == "pnpm"

    def test_the_rust_toolchain_is_installed_in_the_shell_folder(self) -> None:
        steps = self.steps_running("rustup toolchain install")
        assert len(steps) == 1
        assert steps[0]["working-directory"] == self.SHELL

    def test_the_webkit_dependency_is_installed_on_ubuntu_only(self) -> None:
        steps = self.steps_running("libwebkit2gtk-4.1-dev")
        assert len(steps) == 1
        assert "ubuntu" in str(steps[0]["if"])

    def test_dependencies_are_installed_from_the_frozen_lockfile(self) -> None:
        assert any("pnpm install --frozen-lockfile" in run for run in self.runs())

    def test_the_shell_is_built_without_bundling(self) -> None:
        assert any("pnpm --filter @swarm/desktop tauri build --no-bundle" in run for run in self.runs())

    @pytest.mark.parametrize("command", ["cargo fmt --check", "cargo clippy --all-targets --locked -- -D warnings"])
    def test_the_rust_checks_run_on_ubuntu_only_in_the_shell_folder(self, command: str) -> None:
        steps = self.steps_running(command)
        assert len(steps) == 1
        assert "ubuntu" in str(steps[0]["if"])
        assert steps[0]["working-directory"] == self.SHELL

    def test_no_run_step_interpolates_an_expression(self) -> None:
        for run in self.runs():
            assert "${{" not in run
