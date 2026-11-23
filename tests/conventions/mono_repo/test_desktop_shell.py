from __future__ import annotations

# Standard library imports
import json
import re
import tomllib
from pathlib import Path
from typing import ClassVar, Dict, List

# Third-party imports
import pytest
from pydantic import JsonValue

# First-party imports
from tests.conventions.mono_repo.helpers import repo_root


class TestDesktopShell:
    EXACT_VERSION: ClassVar[str] = r"=?2\.\d+\.\d+"
    GROUND_CONTROL_WINDOW: ClassVar[Dict[str, JsonValue]] = {
        "label": "ground-control",
        "url": "ground-control/index.html",
        "title": "⚙️ Swarm · Ground control",
        "width": 1280,
        "height": 800,
    }
    MISSION_STUDIO_WINDOW: ClassVar[Dict[str, JsonValue]] = {
        "label": "mission-studio",
        "url": "mission-studio/index.html",
        "title": "⚙️ Swarm · Mission studio",
        "width": 1280,
        "height": 800,
    }
    CLIPPY_LINTS: ClassVar[Dict[str, str]] = {"all": "deny", "pedantic": "warn"}
    ICONS: ClassVar[List[str]] = [
        "icons/32x32.png",
        "icons/128x128.png",
        "icons/128x128@2x.png",
        "icons/icon.icns",
        "icons/icon.ico",
    ]

    def shell(self) -> Path:
        return repo_root() / "frontends" / "desktop" / "src-tauri"

    def cargo(self) -> Dict[str, JsonValue]:
        path = self.shell() / "Cargo.toml"
        assert path.is_file(), "frontends/desktop/src-tauri/Cargo.toml is missing."
        return tomllib.loads(path.read_text(encoding="utf-8"))

    def conf(self) -> Dict[str, JsonValue]:
        path = self.shell() / "tauri.conf.json"
        assert path.is_file(), "frontends/desktop/src-tauri/tauri.conf.json is missing."
        data = json.loads(path.read_text(encoding="utf-8"))
        assert isinstance(data, dict)
        return data

    def windows(self) -> List[Dict[str, JsonValue]]:
        app = self.conf()["app"]
        assert isinstance(app, dict)
        windows = app["windows"]
        assert isinstance(windows, list)
        return windows

    def test_the_package_is_swarm_desktop(self) -> None:
        assert self.cargo()["package"]["name"] == "swarm-desktop"

    def test_it_has_its_own_empty_workspace_outside_packages_rust(self) -> None:
        assert self.cargo()["workspace"] == {}

    def test_tauri_is_pinned_to_an_exact_2_version(self) -> None:
        version = self.cargo()["dependencies"]["tauri"]
        if isinstance(version, dict):
            version = version["version"]
        assert re.fullmatch(self.EXACT_VERSION, str(version))

    def test_tauri_build_is_pinned_to_an_exact_2_version(self) -> None:
        version = self.cargo()["build-dependencies"]["tauri-build"]
        if isinstance(version, dict):
            version = version["version"]
        assert re.fullmatch(self.EXACT_VERSION, str(version))

    def test_the_clippy_lints_match_the_rust_workspace(self) -> None:
        assert self.cargo()["lints"]["clippy"] == self.CLIPPY_LINTS

    @pytest.mark.parametrize("name", ["rust-toolchain.toml", "Cargo.lock", "src/main.rs", "src/lib.rs"])
    def test_the_rust_files_exist(self, name: str) -> None:
        assert (self.shell() / name).is_file()

    def test_the_assemble_script_exists(self) -> None:
        assert (repo_root() / "frontends" / "desktop" / "scripts" / "assemble.ts").is_file()

    def test_the_product_name_and_identifier(self) -> None:
        conf = self.conf()
        assert conf["productName"] == "Swarm"
        assert str(conf["identifier"]).strip()

    def test_the_frontend_dist_is_the_assembled_folder(self) -> None:
        build = self.conf()["build"]
        assert isinstance(build, dict)
        assert build["frontendDist"] == "../dist"

    @pytest.mark.parametrize("needle", ["@swarm/ground-control", "@swarm/mission-studio", "scripts/assemble.ts"])
    def test_the_before_build_command_builds_both_apps_and_assembles(self, needle: str) -> None:
        build = self.conf()["build"]
        assert isinstance(build, dict)
        assert needle in str(build["beforeBuildCommand"])

    def test_there_are_exactly_two_windows(self) -> None:
        assert len(self.windows()) == 2

    def test_the_first_window_is_ground_control(self) -> None:
        window = self.windows()[0]
        for key, value in self.GROUND_CONTROL_WINDOW.items():
            assert window[key] == value

    def test_the_second_window_is_mission_studio(self) -> None:
        window = self.windows()[1]
        for key, value in self.MISSION_STUDIO_WINDOW.items():
            assert window[key] == value

    def test_the_capability_lists_both_windows(self) -> None:
        path = self.shell() / "capabilities" / "default.json"
        assert path.is_file(), "capabilities/default.json is missing."
        data = json.loads(path.read_text(encoding="utf-8"))
        assert isinstance(data, dict)
        assert set(data["windows"]) >= {"ground-control", "mission-studio"}

    @pytest.mark.parametrize("icon", ICONS)
    def test_the_icons_exist(self, icon: str) -> None:
        assert (self.shell() / icon).is_file()
