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
        waits = lines[2:]
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
        waits = [line for line in lines if "kubectl" in line]
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
