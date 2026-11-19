from __future__ import annotations

import re
import subprocess
from typing import ClassVar, List

import pytest
import yaml
from pydantic import JsonValue

from tests.conventions.mono_repo.helpers import repo_root


class TestTerraformLayout:
    MATRIX_FOLDERS: ClassVar[List[str]] = [
        "deploy/terraform/modules/self-hosted/machines",
        "deploy/terraform/modules/self-hosted/network",
        "deploy/terraform/modules/self-hosted/k3s",
        "deploy/terraform/modules/self-hosted/object-storage",
        "deploy/terraform/modules/self-hosted/dns",
        "deploy/terraform/modules/self-hosted/argocd",
        "deploy/terraform/modules/self-hosted/vault",
        "deploy/terraform/modules/self-hosted/cell",
        "deploy/terraform/modules/self-hosted/cell-application",
        "deploy/terraform/cells/dev",
        "deploy/terraform/cells/dev-branch",
    ]

    def tracked_files(self) -> List[str]:
        result = subprocess.run(
            ["git", "ls-files", "deploy/terraform"],
            cwd=repo_root(),
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.splitlines()

    @pytest.mark.parametrize(
        "module",
        ["machines", "network", "k3s", "object-storage", "dns", "argocd", "vault", "cell", "cell-application"],
    )
    @pytest.mark.parametrize("name", ["main.tf", "variables.tf", "outputs.tf", "versions.tf"])
    def test_each_module_has_its_files(self, module: str, name: str) -> None:
        path = repo_root() / "deploy" / "terraform" / "modules" / "self-hosted" / module / name
        assert path.is_file()

    @pytest.mark.parametrize(
        "name",
        ["main.tf", "variables.tf", "outputs.tf", "versions.tf", "terraform.tfvars.example", ".terraform.lock.hcl"],
    )
    def test_the_dev_cell_has_its_files(self, name: str) -> None:
        assert (repo_root() / "deploy" / "terraform" / "cells" / "dev" / name).is_file()

    def test_the_dev_cell_declares_an_empty_partial_backend(self) -> None:
        path = repo_root() / "deploy" / "terraform" / "cells" / "dev" / "versions.tf"
        assert path.is_file(), "cells/dev/versions.tf is missing."
        assert re.search(r'backend\s+"s3"\s*\{\s*\}', path.read_text(encoding="utf-8"))

    @pytest.mark.parametrize(
        "name",
        [
            "main.tf",
            "variables.tf",
            "outputs.tf",
            "versions.tf",
            "providers.tf",
            "terraform.tfvars.example",
            ".terraform.lock.hcl",
        ],
    )
    def test_the_dev_branch_cell_has_its_files(self, name: str) -> None:
        assert (repo_root() / "deploy" / "terraform" / "cells" / "dev-branch" / name).is_file()

    def test_the_dev_branch_cell_declares_an_empty_partial_backend(self) -> None:
        path = repo_root() / "deploy" / "terraform" / "cells" / "dev-branch" / "versions.tf"
        assert path.is_file(), "cells/dev-branch/versions.tf is missing."
        assert re.search(r'backend\s+"s3"\s*\{\s*\}', path.read_text(encoding="utf-8"))

    def test_the_check_matrix_covers_every_module_and_root(self) -> None:
        path = repo_root() / ".github" / "workflows" / "terraform.yml"
        assert path.is_file(), "terraform.yml is missing."
        workflow: JsonValue = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert isinstance(workflow, dict), "terraform.yml is not a mapping."
        jobs = workflow.get("jobs")
        assert isinstance(jobs, dict), "terraform.yml has no jobs."
        check = jobs.get("check")
        assert isinstance(check, dict), "terraform.yml has no check job."
        strategy = check.get("strategy")
        assert isinstance(strategy, dict), "The check job has no strategy."
        matrix = strategy.get("matrix")
        assert isinstance(matrix, dict), "The check job has no matrix."
        folders = matrix.get("folder")
        assert isinstance(folders, list), "The matrix has no folder list."
        missing = [folder for folder in self.MATRIX_FOLDERS if folder not in folders]
        assert missing == []

    def test_no_state_or_variable_file_is_tracked(self) -> None:
        tracked = self.tracked_files()
        assert tracked, "No Terraform file is tracked."
        forbidden = [name for name in tracked if name.endswith((".tfstate", ".tfvars")) or ".tfstate." in name]
        assert forbidden == []

    @pytest.mark.parametrize(
        "line", [".terraform/", "*.tfstate", "*.tfstate.*", "*.tfvars", "!*.tfvars.example", "deploy/charts/*/charts/"]
    )
    def test_gitignore_holds_the_line(self, line: str) -> None:
        lines = (repo_root() / ".gitignore").read_text(encoding="utf-8").splitlines()
        assert line in [item.strip() for item in lines]

    def test_the_workflow_plans_on_terraform_changes(self) -> None:
        path = repo_root() / ".github" / "workflows" / "terraform.yml"
        assert path.is_file(), "terraform.yml is missing."
        text = path.read_text(encoding="utf-8")
        assert "terraform plan" in text
        assert "deploy/terraform/**" in text
