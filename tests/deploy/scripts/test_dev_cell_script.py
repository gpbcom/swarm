from __future__ import annotations

# Standard library imports
import hashlib
import os
import re
import subprocess
from pathlib import Path
from typing import ClassVar, Dict, List, Optional

# Third-party imports
import pytest


class TestDevCellScript:
    ROOT: ClassVar[Path] = Path(__file__).resolve().parents[3]
    SCRIPT: ClassVar[str] = "deploy/scripts/dev-cell.sh"
    BASH: ClassVar[str] = "bash"
    DRY_RUN: ClassVar[str] = "--dry-run"
    UP: ClassVar[str] = "up"
    DOWN: ClassVar[str] = "down"
    BACKEND_VAR: ClassVar[str] = "DEV_CELL_BACKEND_CONFIG"
    VAR_FILE_VAR: ClassVar[str] = "DEV_CELL_VAR_FILE"
    TIMEOUT_VAR: ClassVar[str] = "DEV_CELL_TIMEOUT"
    BACKEND_PATH: ClassVar[str] = "/nonexistent/backend.tfbackend"
    VAR_FILE_PATH: ClassVar[str] = "/nonexistent/dev-branch.tfvars"
    CHDIR: ClassVar[str] = "-chdir=deploy/terraform/cells/dev-branch"
    PREFIX: ClassVar[str] = "+ "
    BRANCH: ClassVar[str] = "feature/Add_Thing"
    SLUG_MAX: ClassVar[int] = 30
    HASH_LENGTH: ClassVar[int] = 8
    NAME_MAX: ClassVar[int] = 44
    NAME_PATTERN: ClassVar[str] = r"^[a-z0-9]([-a-z0-9]{0,51}[a-z0-9])?$"
    DEFAULT_TIMEOUT: ClassVar[str] = "--timeout=15m"
    USAGE: ClassVar[str] = "usage"
    BAD_USAGE_CODE: ClassVar[int] = 2
    WAIT_STATES: ClassVar[List[str]] = ["Synced", "Healthy"]
    KUBECTL_RUN: ClassVar[str] = f"{PREFIX}kubectl run"
    UNSIGNED_IMAGE_VAR: ClassVar[str] = "DEV_CELL_UNSIGNED_IMAGE"
    UNSIGNED_IMAGE: ClassVar[str] = "ghcr.io/example/unsigned-probe:test"
    DEFAULT_IMAGE_PREFIX: ClassVar[str] = "ghcr.io/gpbcom/swarm/"
    ACCEPTED_MESSAGE: ClassVar[str] = "accepted an unsigned image"
    FAKE_TOOLS: ClassVar[List[str]] = ["terraform", "kubectl"]
    FAKE_TOOL_SCRIPT: ClassVar[str] = '#!/usr/bin/env bash\nif [ "$1" = run ]; then exit {run_code}; fi\nexit 0\n'

    def cell_name(self, branch: str) -> str:
        slug = re.sub(r"[^a-z0-9]+", "-", branch.lower())[: self.SLUG_MAX].strip("-")
        digest = hashlib.sha256(branch.encode("utf-8")).hexdigest()[: self.HASH_LENGTH]
        return f"cell-{slug}-{digest}"

    def environment(self, drop: Optional[str] = None, timeout: Optional[str] = None) -> Dict[str, str]:
        env = dict(os.environ)
        env[self.BACKEND_VAR] = self.BACKEND_PATH
        env[self.VAR_FILE_VAR] = self.VAR_FILE_PATH
        env.pop(self.TIMEOUT_VAR, None)
        if timeout is not None:
            env[self.TIMEOUT_VAR] = timeout
        if drop is not None:
            env.pop(drop)
        return env

    def run_script(
        self, arguments: List[str], env: Optional[Dict[str, str]] = None
    ) -> subprocess.CompletedProcess[str]:
        command = [self.BASH, self.SCRIPT, self.DRY_RUN, *arguments]
        return subprocess.run(
            command,
            cwd=self.ROOT,
            env=env if env is not None else self.environment(),
            capture_output=True,
            text=True,
            check=False,
        )

    def run_with_fakes(
        self, tmp_path: Path, run_code: int, image: Optional[str] = None
    ) -> subprocess.CompletedProcess[str]:
        bin_dir = tmp_path / "bin"
        bin_dir.mkdir()
        for tool in self.FAKE_TOOLS:
            tool_path = bin_dir / tool
            tool_path.write_text(self.FAKE_TOOL_SCRIPT.format(run_code=run_code), encoding="utf-8")
            tool_path.chmod(0o755)
        env = self.environment()
        env["PATH"] = f"{bin_dir}{os.pathsep}{env['PATH']}"
        env.pop(self.UNSIGNED_IMAGE_VAR, None)
        if image is not None:
            env[self.UNSIGNED_IMAGE_VAR] = image
        return subprocess.run(
            [self.BASH, self.SCRIPT, self.UP, self.BRANCH],
            cwd=self.ROOT,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )

    def commands(self, arguments: List[str], env: Optional[Dict[str, str]] = None) -> List[str]:
        result = self.run_script(arguments, env)
        assert result.returncode == 0, result.stderr
        return [line for line in result.stdout.splitlines() if line.startswith(self.PREFIX)]

    def init_line(self, cell: str) -> str:
        return (
            f"{self.PREFIX}terraform {self.CHDIR} init -backend-config={self.BACKEND_PATH} "
            f"-backend-config=key=dev-branch/{cell}.tfstate"
        )

    def terraform_line(self, verb: str, branch: str, cell: str) -> str:
        return (
            f"{self.PREFIX}terraform {self.CHDIR} {verb} -auto-approve -var-file={self.VAR_FILE_PATH} "
            f"-var=branch={branch} -var=cell_name={cell}"
        )

    def test_up_initialises_applies_then_waits_for_argo_cd(self) -> None:
        cell = self.cell_name(self.BRANCH)
        lines = self.commands([self.UP, self.BRANCH])
        assert lines[0] == self.init_line(cell)
        assert lines[1] == self.terraform_line("apply", self.BRANCH, cell)
        waits = [line for line in lines[2:] if " wait " in line]
        assert len(waits) == len(self.WAIT_STATES)
        for line, state in zip(waits, self.WAIT_STATES):
            assert line.startswith(f"{self.PREFIX}kubectl")
            assert " wait " in line
            assert f"application/{cell}" in line
            assert "argocd" in line
            assert state in line
            assert self.DEFAULT_TIMEOUT in line.split()

    def test_the_wait_timeout_can_be_set(self) -> None:
        lines = self.commands([self.UP, self.BRANCH], self.environment(timeout="3m"))
        waits = [line for line in lines if " wait " in line]
        assert len(waits) == len(self.WAIT_STATES)
        assert all("--timeout=3m" in line.split() for line in waits)
        assert not any(self.DEFAULT_TIMEOUT in line.split() for line in waits)

    def test_down_initialises_then_destroys_without_waiting(self) -> None:
        cell = self.cell_name(self.BRANCH)
        lines = self.commands([self.DOWN, self.BRANCH])
        assert lines == [self.init_line(cell), self.terraform_line("destroy", self.BRANCH, cell)]
        assert not any("kubectl" in line for line in lines)

    def test_a_long_branch_gives_a_valid_short_name(self) -> None:
        branch = "feature/" + "x" * 192
        assert len(branch) == 200
        cell = self.cell_name(branch)
        lines = self.commands([self.UP, branch])
        assert lines[0] == self.init_line(cell)
        assert len(cell) <= self.NAME_MAX
        assert re.match(self.NAME_PATTERN, cell)

    def test_branches_that_differ_only_by_punctuation_get_different_names(self) -> None:
        first = self.commands([self.UP, "feature/a_b"])[0]
        second = self.commands([self.UP, "feature/a-b"])[0]
        assert first != second
        assert self.cell_name("feature/a_b") != self.cell_name("feature/a-b")

    @pytest.mark.parametrize(
        "arguments",
        [[], [UP], [DOWN], ["restart", "feature/x"]],
        ids=["no_action", "up_without_branch", "down_without_branch", "unknown_action"],
    )
    def test_bad_arguments_exit_with_code_2_and_a_usage_line(self, arguments: List[str]) -> None:
        result = self.run_script(arguments)
        assert result.returncode == self.BAD_USAGE_CODE
        assert self.USAGE in result.stderr.lower()

    @pytest.mark.parametrize("variable", [BACKEND_VAR, VAR_FILE_VAR])
    def test_a_missing_variable_exits_with_code_2_and_is_named(self, variable: str) -> None:
        result = self.run_script([self.UP, self.BRANCH], self.environment(drop=variable))
        assert result.returncode == self.BAD_USAGE_CODE
        assert variable in result.stderr

    def test_up_ends_with_a_server_side_probe_of_an_unsigned_image(self) -> None:
        cell = self.cell_name(self.BRANCH)
        lines = self.commands([self.UP, self.BRANCH])
        probes = [line for line in lines if line.startswith(self.KUBECTL_RUN)]
        assert len(probes) == 1
        assert lines[-1] == probes[0]
        assert lines.index(probes[0]) == 2 + len(self.WAIT_STATES)
        words = probes[0].split()
        assert "--namespace" in words
        assert words[words.index("--namespace") + 1] == cell
        assert "--dry-run=server" in words
        assert "--restart=Never" in words

    def test_the_probe_image_defaults_to_one_of_the_project_registry(self) -> None:
        env = self.environment()
        env.pop(self.UNSIGNED_IMAGE_VAR, None)
        probe = self.commands([self.UP, self.BRANCH], env)[-1]
        images = [word for word in probe.split() if word.startswith("--image=")]
        assert len(images) == 1
        assert images[0].removeprefix("--image=").startswith(self.DEFAULT_IMAGE_PREFIX)

    def test_the_probe_image_can_be_set(self) -> None:
        env = self.environment()
        env[self.UNSIGNED_IMAGE_VAR] = self.UNSIGNED_IMAGE
        probe = self.commands([self.UP, self.BRANCH], env)[-1]
        assert f"--image={self.UNSIGNED_IMAGE}" in probe.split()

    def test_down_prints_no_probe(self) -> None:
        lines = self.commands([self.DOWN, self.BRANCH])
        assert not any(line.startswith(self.KUBECTL_RUN) for line in lines)

    def test_up_fails_when_the_cell_accepts_an_unsigned_image(self, tmp_path: Path) -> None:
        result = self.run_with_fakes(tmp_path, run_code=0)
        assert result.returncode != 0
        assert self.ACCEPTED_MESSAGE in result.stderr

    def test_up_succeeds_when_the_cell_refuses_an_unsigned_image(self, tmp_path: Path) -> None:
        result = self.run_with_fakes(tmp_path, run_code=1)
        assert result.returncode == 0, result.stderr
