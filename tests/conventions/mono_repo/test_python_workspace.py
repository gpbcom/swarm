from __future__ import annotations

import tomllib
from typing import Dict, List

import pytest
from pydantic import JsonValue

from tests.conventions.mono_repo.helpers import SERVICE_LAYERS, repo_root


class TestPythonWorkspace:
    def load_root(self) -> Dict[str, JsonValue]:
        path = repo_root() / "pyproject.toml"
        assert path.is_file(), "The root pyproject.toml is missing."
        return tomllib.loads(path.read_text(encoding="utf-8"))

    def test_the_root_pyproject_has_no_project_table(self) -> None:
        assert "project" not in self.load_root()

    @pytest.mark.parametrize("member", ["services/*", "packages/python/*"])
    def test_the_uv_workspace_lists_its_members(self, member: str) -> None:
        tool = self.load_root().get("tool", {})
        assert isinstance(tool, dict)
        members: List[str] = tool.get("uv", {}).get("workspace", {}).get("members", [])
        assert member in members

    @pytest.mark.parametrize("tool_name", ["ruff", "mypy", "pytest", "pytest-xdist", "pytest-asyncio", "maturin"])
    def test_the_dev_group_lists_the_tool(self, tool_name: str) -> None:
        group = self.load_root().get("dependency-groups", {})
        assert isinstance(group, dict)
        names = [
            str(item).split(">")[0].split("=")[0].split("<")[0].split("[")[0].strip() for item in group.get("dev", [])
        ]
        assert tool_name in names

    def test_the_root_src_folder_does_not_exist(self) -> None:
        assert not (repo_root() / "src").exists()

    def test_there_is_exactly_one_lock_file_at_the_root(self) -> None:
        root = repo_root()
        assert (root / "uv.lock").is_file()
        assert not list((root / "services").rglob("uv.lock"))
        assert not list((root / "packages").rglob("uv.lock"))

    def test_the_python_packages_folder_exists(self) -> None:
        assert (repo_root() / "packages" / "python").is_dir()

    def test_the_gateway_declares_its_name_and_console_script(self) -> None:
        path = repo_root() / "services" / "gateway" / "pyproject.toml"
        assert path.is_file(), "The gateway pyproject.toml is missing."
        data = tomllib.loads(path.read_text(encoding="utf-8"))
        assert data["project"]["name"] == "swarm-gateway"
        assert data["project"]["scripts"]["swarm-gateway"] == "gateway.api.cli.main:main"

    @pytest.mark.parametrize("layer", ["api", "service", "storage", "clients", "models"])
    def test_the_gateway_has_the_layer_package(self, layer: str) -> None:
        assert (repo_root() / "services" / "gateway" / "src" / "gateway" / layer / "__init__.py").is_file()

    def test_no_service_has_a_top_level_layer_package(self) -> None:
        offenders = [
            str(path)
            for src in (repo_root() / "services").glob("*/src")
            for layer in SERVICE_LAYERS
            for path in [src / layer]
            if path.exists()
        ]
        assert offenders == []
        assert list((repo_root() / "services").glob("*/src/gateway")), "No service source package was found."
