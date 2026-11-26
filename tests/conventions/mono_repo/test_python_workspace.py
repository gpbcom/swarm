from __future__ import annotations

# Standard library imports
import re
import tomllib
from pathlib import Path
from typing import ClassVar, Dict, List

# Third-party imports
import pytest
from pydantic import JsonValue

# First-party imports
from tests.conventions.mono_repo.helpers import SERVICE_LAYERS, repo_root


class TestPythonWorkspace:
    NEW_SERVICES: ClassVar[List[str]] = ["missions", "fleet"]
    ALL_SERVICES: ClassVar[List[str]] = ["gateway", "missions", "fleet"]
    NEW_PACKAGES: ClassVar[List[str]] = ["swarm-storage", "swarm-rest", "swarm-web", "swarm-nats"]
    SCRIPT_ENTRIES: ClassVar[List[str]] = ["serve", "openapi", "migrate"]
    LAYERS: ClassVar[List[str]] = ["api", "service", "storage", "clients", "models"]
    GATEWAY_SCRIPT: ClassVar[str] = "gateway.api.cli.main:main"
    STORAGE_DEPENDENCIES: ClassVar[List[str]] = ["asyncpg", "alembic", "sqlalchemy", "swarm-models"]
    WEB_DEPENDENCIES: ClassVar[List[str]] = ["fastapi", "uvicorn"]
    SHARED_DEPENDENCIES: ClassVar[List[str]] = ["swarm-storage", "swarm-rest"]
    FIRST_PARTY: ClassVar[List[str]] = ["missions", "fleet", "swarm_storage", "swarm_rest", "swarm_web"]
    TEST_PATHS: ClassVar[List[str]] = [
        "services/missions/tests",
        "services/fleet/tests",
        "packages/python/swarm-rest/tests",
    ]
    MYPY_FILES: ClassVar[List[str]] = [
        "services/missions/src",
        "services/fleet/src",
        "backend/swarm-storage/src",
        "packages/python/swarm-rest/src",
        "backend/libs/swarm-web/src",
        "backend/libs/swarm-nats/src",
    ]
    DISTRIBUTION_SEPARATORS: ClassVar[str] = r"[\[<>=!~;@ ]"

    def load_toml(self, path: Path) -> Dict[str, JsonValue]:
        assert path.is_file(), f"{path} is missing."
        return tomllib.loads(path.read_text(encoding="utf-8"))

    def table(self, data: Dict[str, JsonValue], *keys: str) -> Dict[str, JsonValue]:
        current: JsonValue = data
        for key in keys:
            assert isinstance(current, dict), f"{key} is not under a table."
            current = current.get(key, {})
        assert isinstance(current, dict)
        return current

    def distribution_names(self, items: JsonValue) -> List[str]:
        assert isinstance(items, list)
        return [re.split(self.DISTRIBUTION_SEPARATORS, str(item), maxsplit=1)[0].strip() for item in items]

    def project_file(self, kind: str, name: str) -> Path:
        return repo_root() / kind / name / "pyproject.toml"

    def package_file(self, name: str) -> Path:
        for kind in ("packages/python", "backend", "backend/libs"):
            path = self.project_file(kind, name)
            if path.is_file():
                return path
        return self.project_file("packages/python", name)

    def dependencies_of(self, path: Path) -> List[str]:
        project = self.table(self.load_toml(path), "project")
        return self.distribution_names(project.get("dependencies", []))

    def load_root(self) -> Dict[str, JsonValue]:
        path = repo_root() / "pyproject.toml"
        assert path.is_file(), "The root pyproject.toml is missing."
        return tomllib.loads(path.read_text(encoding="utf-8"))

    def test_the_root_pyproject_has_no_project_table(self) -> None:
        assert "project" not in self.load_root()

    @pytest.mark.parametrize(
        "member", ["services/*", "packages/python/*", "backend/libs/*", "backend/swarm-*", "scripts"]
    )
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

    @pytest.mark.parametrize("service", NEW_SERVICES)
    def test_a_new_service_declares_its_name_and_module(self, service: str) -> None:
        data = self.load_toml(self.project_file("services", service))
        assert self.table(data, "project")["name"] == f"swarm-{service}"
        assert self.table(data, "tool", "uv", "build-backend")["module-name"] == service

    @pytest.mark.parametrize("package", NEW_PACKAGES)
    def test_a_new_package_declares_its_name_and_module(self, package: str) -> None:
        data = self.load_toml(self.package_file(package))
        assert self.table(data, "project")["name"] == package
        assert self.table(data, "tool", "uv", "build-backend")["module-name"] == package.replace("-", "_")

    @pytest.mark.parametrize("service", ALL_SERVICES)
    @pytest.mark.parametrize("entry", SCRIPT_ENTRIES)
    def test_a_service_declares_its_console_scripts(self, service: str, entry: str) -> None:
        scripts = self.table(self.load_toml(self.project_file("services", service)), "project", "scripts")
        assert scripts[f"swarm-{service}-{entry}"] == f"{service}.api.cli.{entry}_main:main"

    def test_the_gateway_keeps_its_console_script(self) -> None:
        scripts = self.table(self.load_toml(self.project_file("services", "gateway")), "project", "scripts")
        assert scripts["swarm-gateway"] == self.GATEWAY_SCRIPT

    @pytest.mark.parametrize("service", NEW_SERVICES)
    @pytest.mark.parametrize("layer", LAYERS)
    def test_a_new_service_has_the_layer_package(self, service: str, layer: str) -> None:
        assert (repo_root() / "services" / service / "src" / service / layer / "__init__.py").is_file()

    @pytest.mark.parametrize("dependency", STORAGE_DEPENDENCIES)
    def test_swarm_storage_depends_on(self, dependency: str) -> None:
        assert dependency in self.dependencies_of(self.package_file("swarm-storage"))

    @pytest.mark.parametrize("dependency", WEB_DEPENDENCIES)
    def test_swarm_web_depends_on(self, dependency: str) -> None:
        assert dependency in self.dependencies_of(self.package_file("swarm-web"))

    @pytest.mark.parametrize("service", ALL_SERVICES)
    @pytest.mark.parametrize("dependency", SHARED_DEPENDENCIES)
    def test_a_service_depends_on_the_shared_package(self, service: str, dependency: str) -> None:
        assert dependency in self.dependencies_of(self.project_file("services", service))

    @pytest.mark.parametrize("name", FIRST_PARTY)
    def test_the_root_lists_the_first_party_module(self, name: str) -> None:
        isort = self.table(self.load_root(), "tool", "ruff", "lint", "isort")
        assert name in isort["known-first-party"]

    @pytest.mark.parametrize("path", TEST_PATHS)
    def test_the_root_lists_the_test_path(self, path: str) -> None:
        options = self.table(self.load_root(), "tool", "pytest", "ini_options")
        assert path in options["testpaths"]

    @pytest.mark.parametrize("path", MYPY_FILES)
    def test_the_root_lists_the_mypy_files(self, path: str) -> None:
        assert path in self.table(self.load_root(), "tool", "mypy")["files"]
