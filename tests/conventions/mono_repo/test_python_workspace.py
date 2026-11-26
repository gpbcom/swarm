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
    APPS: ClassVar[List[str]] = ["gateway", "missions", "fleet", "simulator", "flight-engine"]
    DOMAINS: ClassVar[Dict[str, str]] = {
        "gateway": "gateway",
        "missions": "missions",
        "fleet": "fleet",
        "simulator": "simulation",
        "flight-engine": "flight",
    }
    ROUTERS: ClassVar[Dict[str, str]] = {
        "gateway": "gateway_router.py",
        "missions": "missions_router.py",
        "fleet": "fleet_router.py",
        "simulator": "simulation_router.py",
        "flight-engine": "flight_engine_router.py",
    }
    MEMBERS: ClassVar[List[str]] = ["backend/libs/*", "backend/swarm-*", "backend/apps/*", "scripts"]
    OLD_MEMBERS: ClassVar[List[str]] = ["services/*", "packages/python/*"]
    NEW_PACKAGES: ClassVar[List[str]] = ["swarm-storage", "swarm-api", "swarm-web", "swarm-nats"]
    SERVE_ENTRY: ClassVar[str] = "serve"
    APP_FILES: ClassVar[List[str]] = ["__init__.py", "main.py"]
    STORAGE_DEPENDENCIES: ClassVar[List[str]] = ["asyncpg", "alembic", "sqlalchemy", "swarm-models"]
    WEB_DEPENDENCIES: ClassVar[List[str]] = ["fastapi", "uvicorn"]
    APP_DEPENDENCIES: ClassVar[List[str]] = ["swarm-api", "swarm-logging", "swarm-models", "swarm-web"]
    FIRST_PARTY: ClassVar[List[str]] = [
        "swarm_gateway",
        "swarm_missions",
        "swarm_fleet",
        "swarm_storage",
        "swarm_web",
        "swarm_scripts",
        "swarm_simulator",
        "swarm_flight_engine",
    ]
    TEST_PATHS: ClassVar[List[str]] = ["tests"]
    MYPY_FILES: ClassVar[List[str]] = [
        "backend/apps/gateway/src",
        "backend/apps/missions/src",
        "backend/apps/fleet/src",
        "backend/apps/simulator/src",
        "backend/apps/flight-engine/src",
        "backend/swarm-storage/src",
        "backend/libs/swarm-web/src",
        "backend/libs/swarm-nats/src",
        "scripts/src",
    ]
    GONE: ClassVar[List[str]] = [
        "services/gateway",
        "services/missions",
        "services/fleet",
        "packages/python/swarm-rest",
        "services/simulator",
        "services/flight-engine",
        "packages/python/swarm-live",
        "packages/python/swarm-i18n",
        "services",
        "packages/python",
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
        for kind in ("backend", "backend/libs"):
            path = self.project_file(kind, name)
            if path.is_file():
                return path
        return self.project_file("backend", name)

    def dependencies_of(self, path: Path) -> List[str]:
        project = self.table(self.load_toml(path), "project")
        return self.distribution_names(project.get("dependencies", []))

    def load_root(self) -> Dict[str, JsonValue]:
        path = repo_root() / "pyproject.toml"
        assert path.is_file(), "The root pyproject.toml is missing."
        return tomllib.loads(path.read_text(encoding="utf-8"))

    def test_the_root_pyproject_has_no_project_table(self) -> None:
        assert "project" not in self.load_root()

    def members(self) -> List[str]:
        tool = self.load_root().get("tool", {})
        assert isinstance(tool, dict)
        members: List[str] = tool.get("uv", {}).get("workspace", {}).get("members", [])
        return members

    @pytest.mark.parametrize("member", MEMBERS)
    def test_the_uv_workspace_lists_its_members(self, member: str) -> None:
        assert member in self.members()

    @pytest.mark.parametrize("member", OLD_MEMBERS)
    def test_the_uv_workspace_no_longer_lists_the_old_layout(self, member: str) -> None:
        assert member not in self.members()

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
        assert not list((root / "backend").rglob("uv.lock"))

    def test_the_services_and_the_python_packages_folders_are_gone(self) -> None:
        assert not (repo_root() / "services").exists()
        assert not (repo_root() / "packages" / "python").exists()

    def app_folder(self, app: str) -> Path:
        return repo_root() / "backend" / "apps" / app

    @pytest.mark.parametrize("path", GONE)
    def test_the_old_services_and_swarm_rest_are_gone(self, path: str) -> None:
        assert not (repo_root() / path).exists()

    def test_no_service_has_a_top_level_layer_package(self) -> None:
        offenders = [
            str(path)
            for src in (repo_root() / "services").glob("*/src")
            for layer in SERVICE_LAYERS
            for path in [src / layer]
            if path.exists()
        ]
        assert offenders == []
        assert list((repo_root() / "backend" / "apps").glob("*/src/swarm_*")), "No app source package was found."

    def module_of(self, app: str) -> str:
        return "swarm_" + app.replace("-", "_")

    @pytest.mark.parametrize("app", APPS)
    def test_an_app_declares_its_name_its_module_and_its_domain(self, app: str) -> None:
        data = self.load_toml(self.app_folder(app) / "pyproject.toml")
        assert self.table(data, "project")["name"] == f"swarm-{app}"
        assert self.table(data, "tool", "uv", "build-backend")["module-name"] == self.module_of(app)
        assert self.table(data, "tool", "swarm")["domains"] == [self.DOMAINS[app]]

    @pytest.mark.parametrize("package", NEW_PACKAGES)
    def test_a_new_package_declares_its_name_and_module(self, package: str) -> None:
        data = self.load_toml(self.package_file(package))
        assert self.table(data, "project")["name"] == package
        assert self.table(data, "tool", "uv", "build-backend")["module-name"] == package.replace("-", "_")

    @pytest.mark.parametrize("app", APPS)
    def test_an_app_declares_only_its_serve_script(self, app: str) -> None:
        scripts = self.table(self.load_toml(self.app_folder(app) / "pyproject.toml"), "project", "scripts")
        assert scripts == {f"swarm-{app}-{self.SERVE_ENTRY}": f"{self.module_of(app)}.main:main"}

    @pytest.mark.parametrize("app", APPS)
    def test_an_app_holds_only_its_main(self, app: str) -> None:
        module = self.app_folder(app) / "src" / self.module_of(app)
        assert sorted(path.name for path in module.glob("*.py")) == self.APP_FILES

    @pytest.mark.parametrize("app", APPS)
    def test_the_domain_of_an_app_has_its_versioned_router(self, app: str) -> None:
        api = repo_root() / "backend" / "swarm-api" / "src" / "swarm_api" / "v1"
        router = api / self.DOMAINS[app] / self.ROUTERS[app]
        assert router.is_file()

    @pytest.mark.parametrize("dependency", STORAGE_DEPENDENCIES)
    def test_swarm_storage_depends_on(self, dependency: str) -> None:
        assert dependency in self.dependencies_of(self.package_file("swarm-storage"))

    @pytest.mark.parametrize("dependency", WEB_DEPENDENCIES)
    def test_swarm_web_depends_on(self, dependency: str) -> None:
        assert dependency in self.dependencies_of(self.package_file("swarm-web"))

    @pytest.mark.parametrize("app", APPS)
    @pytest.mark.parametrize("dependency", APP_DEPENDENCIES)
    def test_an_app_depends_on_the_layer_package(self, app: str, dependency: str) -> None:
        assert dependency in self.dependencies_of(self.app_folder(app) / "pyproject.toml")

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
