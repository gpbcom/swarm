from __future__ import annotations

# Standard library imports
import json
import re
from pathlib import Path
from typing import ClassVar, Dict, List

# Third-party imports
import pytest
from pydantic import JsonValue

# First-party imports
from tests.conventions.mono_repo.helpers import repo_root


class TestFrontendWorkspace:
    TOKENS: ClassVar[str] = "frontend/packages/tokens"
    UI: ClassVar[str] = "frontend/packages/ui"
    MAPS: ClassVar[str] = "frontend/packages/maps"
    LIVE: ClassVar[str] = "frontend/packages/live"
    GROUND_CONTROL: ClassVar[str] = "frontend/apps/ground-control"
    E2E: ClassVar[str] = "qa/e2e"
    MAP_DEPENDENCIES: ClassVar[List[str]] = [
        "maplibre-gl",
        "pmtiles",
        "@deck.gl/core",
        "@deck.gl/layers",
        "@deck.gl/mapbox",
    ]
    DESKTOP: ClassVar[str] = "frontend/apps/desktop"
    APPS: ClassVar[List[str]] = [
        "frontend/apps/ground-control",
        "frontend/apps/mission-studio",
        "frontend/apps/back-office",
        "frontend/apps/client-portal",
    ]
    NAMES: ClassVar[Dict[str, str]] = {
        "frontend/packages/tokens": "@swarm/tokens",
        "frontend/packages/ui": "@swarm/ui",
        "frontend/packages/maps": "@swarm/maps",
        "frontend/packages/live": "@swarm/live",
        "frontend/apps/ground-control": "@swarm/ground-control",
        "frontend/apps/mission-studio": "@swarm/mission-studio",
        "frontend/apps/back-office": "@swarm/back-office",
        "frontend/apps/client-portal": "@swarm/client-portal",
        "frontend/apps/desktop": "@swarm/desktop",
    }
    PROJECTS: ClassVar[List[str]] = list(NAMES)
    CONFIGURED: ClassVar[List[str]] = [folder for folder in NAMES if folder != "frontend/packages/tokens"]
    WORKSPACE: ClassVar[str] = "workspace:*"
    EXACT_VERSION: ClassVar[str] = r"\d+\.\d+\.\d+(-[0-9A-Za-z.\-]+)?"
    REACT_19: ClassVar[str] = r"[\^~]?19\.\d+\.\d+(-[0-9A-Za-z.\-]+)?"
    TAURI_2: ClassVar[str] = r"2\.\d+\.\d+(-[0-9A-Za-z.\-]+)?"
    DEPENDENCY_SECTIONS: ClassVar[List[str]] = ["dependencies", "devDependencies", "peerDependencies"]

    def path(self, folder: str, name: str) -> Path:
        return repo_root() / folder / name

    def text(self, folder: str, name: str) -> str:
        path = self.path(folder, name)
        assert path.is_file(), f"{folder}/{name} is missing."
        return path.read_text(encoding="utf-8")

    def package(self, folder: str) -> Dict[str, JsonValue]:
        return json.loads(self.text(folder, "package.json"))

    def as_dict(self, value: JsonValue) -> Dict[str, JsonValue]:
        assert isinstance(value, dict)
        return value

    def section(self, folder: str, name: str) -> Dict[str, JsonValue]:
        return self.as_dict(self.package(folder).get(name))

    def react_versions(self, folder: str, name: str) -> List[str]:
        versions: List[str] = []
        for section in self.DEPENDENCY_SECTIONS:
            value = self.package(folder).get(section)
            if isinstance(value, dict) and isinstance(value.get(name), str):
                versions.append(str(value[name]))
        return versions

    @pytest.mark.parametrize("folder", PROJECTS)
    def test_the_package_is_a_private_module_with_its_name(self, folder: str) -> None:
        package = self.package(folder)
        assert package.get("name") == self.NAMES[folder]
        assert package.get("private") is True
        assert package.get("type") == "module"

    @pytest.mark.parametrize("folder", PROJECTS)
    def test_every_dependency_is_a_workspace_link_or_an_exact_version(self, folder: str) -> None:
        for section in ["dependencies", "devDependencies"]:
            value = self.package(folder).get(section)
            for name, version in (self.as_dict(value) if value is not None else {}).items():
                assert isinstance(version, str)
                assert version == self.WORKSPACE or re.fullmatch(self.EXACT_VERSION, version), (
                    f"{folder}: {name} is not pinned: {version!r}."
                )

    @pytest.mark.parametrize("folder", PROJECTS)
    def test_the_lock_file_has_an_importer_for_the_project(self, folder: str) -> None:
        lines = (repo_root() / "pnpm-lock.yaml").read_text(encoding="utf-8").splitlines()
        assert f"  {folder}:" in lines

    @pytest.mark.parametrize("folder", CONFIGURED)
    def test_the_tsconfig_extends_the_shared_base(self, folder: str) -> None:
        tsconfig = json.loads(self.text(folder, "tsconfig.json"))
        assert tsconfig.get("extends") == "@swarm/config/tsconfig.base.json"

    @pytest.mark.parametrize("folder", CONFIGURED)
    def test_the_eslint_configuration_imports_the_shared_one(self, folder: str) -> None:
        assert "@swarm/config/eslint" in self.text(folder, "eslint.config.js")

    @pytest.mark.parametrize("folder", CONFIGURED)
    def test_the_shared_config_is_a_workspace_dev_dependency(self, folder: str) -> None:
        assert self.section(folder, "devDependencies").get("@swarm/config") == self.WORKSPACE

    @pytest.mark.parametrize("folder", CONFIGURED)
    def test_the_project_has_lint_and_typecheck_scripts(self, folder: str) -> None:
        scripts = self.section(folder, "scripts")
        assert "eslint" in str(scripts.get("lint"))
        typecheck = str(scripts.get("typecheck"))
        assert "tsc" in typecheck
        assert "--noEmit" in typecheck

    def test_the_tokens_package_exports_its_stylesheet(self) -> None:
        exports = self.section(self.TOKENS, "exports")
        assert exports.get("./tokens.css") == "./src/tokens.css"

    def test_the_ui_package_exports_its_entry_point_and_styles(self) -> None:
        exports = self.section(self.UI, "exports")
        assert exports.get(".") == "./src/index.ts"
        assert exports.get("./styles.css") == "./src/styles.css"

    def test_the_ui_package_depends_on_the_tokens_and_on_radix(self) -> None:
        dependencies = self.section(self.UI, "dependencies")
        assert dependencies.get("@swarm/tokens") == self.WORKSPACE
        assert any(name.startswith("@radix-ui/react-") for name in dependencies)

    @pytest.mark.parametrize("name", ["react", "react-dom"])
    def test_the_ui_package_uses_react_19(self, name: str) -> None:
        versions = self.react_versions(self.UI, name)
        assert versions, f"{self.UI} does not declare {name}."
        assert all(re.fullmatch(self.REACT_19, version) for version in versions)

    def test_the_ui_package_tests_with_vitest(self) -> None:
        assert "vitest" in str(self.section(self.UI, "scripts").get("test"))

    @pytest.mark.parametrize("folder", APPS)
    def test_an_app_depends_on_the_ui_and_the_tokens(self, folder: str) -> None:
        dependencies = self.section(folder, "dependencies")
        assert dependencies.get("@swarm/ui") == self.WORKSPACE
        assert dependencies.get("@swarm/tokens") == self.WORKSPACE

    @pytest.mark.parametrize("name", ["react", "react-dom"])
    @pytest.mark.parametrize("folder", APPS)
    def test_an_app_uses_react_19(self, folder: str, name: str) -> None:
        version = self.section(folder, "dependencies").get(name)
        assert isinstance(version, str)
        assert re.fullmatch(self.REACT_19, version)

    @pytest.mark.parametrize("folder", APPS)
    def test_an_app_builds_with_vite_and_tests_with_vitest(self, folder: str) -> None:
        scripts = self.section(folder, "scripts")
        assert "vite build" in str(scripts.get("build"))
        assert "vitest" in str(scripts.get("test"))

    @pytest.mark.parametrize("folder", APPS)
    def test_an_app_is_built_for_a_relative_base(self, folder: str) -> None:
        assert re.search(r"""base:\s*["']\./["']""", self.text(folder, "vite.config.ts"))

    def test_the_desktop_shell_pins_the_tauri_cli_to_version_2(self) -> None:
        version = self.section(self.DESKTOP, "devDependencies").get("@tauri-apps/cli")
        assert isinstance(version, str)
        assert re.fullmatch(self.TAURI_2, version)

    def test_the_desktop_shell_exposes_the_tauri_script(self) -> None:
        assert self.section(self.DESKTOP, "scripts").get("tauri") == "tauri"

    def test_the_maps_package_exports_its_entry_point_and_styles(self) -> None:
        exports = self.section(self.MAPS, "exports")
        assert exports.get(".") == "./src/index.ts"
        assert exports.get("./styles.css") == "./src/styles.css"

    @pytest.mark.parametrize("name", MAP_DEPENDENCIES)
    def test_the_maps_package_depends_on_the_map_libraries_with_exact_versions(self, name: str) -> None:
        version = self.section(self.MAPS, "dependencies").get(name)
        assert isinstance(version, str), f"{self.MAPS} does not depend on {name}."
        assert re.fullmatch(self.EXACT_VERSION, version)

    @pytest.mark.parametrize("name", ["react", "react-dom"])
    def test_the_maps_package_uses_react_19(self, name: str) -> None:
        peers = self.section(self.MAPS, "peerDependencies")
        version = peers.get(name)
        assert isinstance(version, str), f"{self.MAPS} does not declare {name} as a peer."
        assert re.fullmatch(self.REACT_19, version)

    def test_the_maps_package_tests_with_vitest(self) -> None:
        assert "vitest" in str(self.section(self.MAPS, "scripts").get("test"))

    def test_the_live_package_depends_on_msgpack_with_an_exact_version(self) -> None:
        version = self.section(self.LIVE, "dependencies").get("@msgpack/msgpack")
        assert isinstance(version, str)
        assert re.fullmatch(self.EXACT_VERSION, version)

    def test_the_live_package_tests_the_files_of_its_sub_folders(self) -> None:
        assert "test/**/*.test.ts" in str(self.section(self.LIVE, "scripts").get("test"))

    @pytest.mark.parametrize("name", ["@swarm/live", "@swarm/maps"])
    def test_ground_control_depends_on_the_live_and_maps_packages(self, name: str) -> None:
        assert self.section(self.GROUND_CONTROL, "dependencies").get(name) == self.WORKSPACE

    def test_ground_control_has_an_e2e_script_running_playwright(self) -> None:
        assert "playwright test" in str(self.section(self.GROUND_CONTROL, "scripts").get("e2e"))

    def test_ground_control_dev_depends_on_the_e2e_package_and_its_playwright_version(self) -> None:
        dev = self.section(self.GROUND_CONTROL, "devDependencies")
        assert dev.get("@swarm/e2e") == self.WORKSPACE
        expected = self.section(self.E2E, "devDependencies").get("@playwright/test")
        assert isinstance(expected, str)
        assert dev.get("@playwright/test") == expected
