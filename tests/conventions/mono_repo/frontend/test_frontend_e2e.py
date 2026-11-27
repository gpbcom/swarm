from __future__ import annotations

# Standard library imports
import json
from functools import partial
from itertools import compress, repeat
from operator import contains
from pathlib import Path
from typing import ClassVar, Dict, List

# Third-party imports
import pytest
from pydantic import JsonValue

# First-party imports
from tests.conventions.mono_repo.helpers import repo_root


class TestFrontendE2e:
    APPS_FOLDER: ClassVar[str] = "frontend/apps"
    E2E_FOLDER: ClassVar[str] = "e2e"
    BACK_OFFICE: ClassVar[str] = "frontend/apps/back-office"
    SHARED_E2E: ClassVar[str] = "qa/e2e"
    PACKAGE: ClassVar[str] = "package.json"
    PLAYWRIGHT_CONFIG: ClassVar[str] = "playwright.config.ts"
    TSCONFIG: ClassVar[str] = "tsconfig.json"
    ENCODING: ClassVar[str] = "utf-8"
    SCRIPTS: ClassVar[str] = "scripts"
    DEV_DEPENDENCIES: ClassVar[str] = "devDependencies"
    INCLUDE: ClassVar[str] = "include"
    PLAYWRIGHT_PACKAGE: ClassVar[str] = "@playwright/test"
    E2E_PACKAGE: ClassVar[str] = "@swarm/e2e"
    WORKSPACE: ClassVar[str] = "workspace:*"
    E2E_SCRIPT: ClassVar[str] = "e2e"
    CAPTURE_SCRIPT: ClassVar[str] = "capture"
    RUN_COMMAND: ClassVar[str] = "playwright test"
    CAPTURE_FLAGS: ClassVar[List[str]] = ["--update-snapshots=all", "--grep-invert @difference"]
    IMPORT_FROM: ClassVar[str] = '"@swarm/e2e"'
    DEFINE: ClassVar[str] = "defineVisualConfig"
    WEB_SERVER: ClassVar[str] = "webServer"
    TSCONFIG_ENTRIES: ClassVar[List[str]] = ["e2e", "playwright.config.ts"]
    SPEC_SUFFIX: ClassVar[str] = ".spec.ts"
    SCREEN_COMPARISON: ClassVar[str] = "toHaveScreenshot("
    FOLDERS: ClassVar[List[str]] = sorted(
        str(path.parent.relative_to(repo_root())) for path in (repo_root() / APPS_FOLDER).glob(f"*/{E2E_FOLDER}")
    )
    SPECS: ClassVar[List[Path]] = sorted((repo_root() / APPS_FOLDER).glob(f"*/{E2E_FOLDER}/*{SPEC_SUFFIX}"))
    SCREEN_SPECS: ClassVar[List[Path]] = list(
        compress(
            SPECS, map(contains, map(partial(Path.read_text, encoding=ENCODING), SPECS), repeat(SCREEN_COMPARISON))
        )
    )
    VISUAL_FOLDERS: ClassVar[List[str]] = sorted(
        {str(spec.parent.parent.relative_to(repo_root())) for spec in SCREEN_SPECS}
    )

    def path(self, folder: str, name: str) -> Path:
        return repo_root() / folder / name

    def text(self, folder: str, name: str) -> str:
        path = self.path(folder, name)
        assert path.is_file(), f"{folder}/{name} is missing."
        return path.read_text(encoding=self.ENCODING)

    def as_dict(self, value: JsonValue) -> Dict[str, JsonValue]:
        assert isinstance(value, dict)
        return value

    def section(self, folder: str, name: str) -> Dict[str, JsonValue]:
        return self.as_dict(json.loads(self.text(folder, self.PACKAGE)).get(name))

    def shared_playwright_version(self) -> JsonValue:
        shared = json.loads(self.text(self.SHARED_E2E, self.PACKAGE))
        return self.as_dict(shared[self.DEV_DEPENDENCIES]).get(self.PLAYWRIGHT_PACKAGE)

    def test_the_back_office_has_an_e2e_folder(self) -> None:
        assert self.BACK_OFFICE in self.FOLDERS

    def test_the_back_office_compares_its_screens(self) -> None:
        assert self.BACK_OFFICE in self.VISUAL_FOLDERS

    @pytest.mark.parametrize("folder", FOLDERS)
    def test_the_e2e_script_runs_playwright(self, folder: str) -> None:
        script = self.section(folder, self.SCRIPTS).get(self.E2E_SCRIPT)
        assert isinstance(script, str)
        assert self.RUN_COMMAND in script

    @pytest.mark.parametrize("folder", VISUAL_FOLDERS)
    def test_the_capture_script_updates_every_snapshot_but_the_differences(self, folder: str) -> None:
        script = self.section(folder, self.SCRIPTS).get(self.CAPTURE_SCRIPT)
        assert isinstance(script, str)
        assert self.RUN_COMMAND in script
        for flag in self.CAPTURE_FLAGS:
            assert flag in script

    @pytest.mark.parametrize("folder", FOLDERS)
    def test_playwright_is_at_the_version_of_the_shared_set_up(self, folder: str) -> None:
        version = self.section(folder, self.DEV_DEPENDENCIES).get(self.PLAYWRIGHT_PACKAGE)
        assert isinstance(version, str)
        assert version == self.shared_playwright_version()

    @pytest.mark.parametrize("folder", FOLDERS)
    def test_the_shared_e2e_package_is_a_workspace_link(self, folder: str) -> None:
        assert self.section(folder, self.DEV_DEPENDENCIES).get(self.E2E_PACKAGE) == self.WORKSPACE

    @pytest.mark.parametrize("folder", FOLDERS)
    def test_the_playwright_config_uses_the_shared_set_up_and_no_web_server(self, folder: str) -> None:
        config = self.text(folder, self.PLAYWRIGHT_CONFIG)
        assert self.IMPORT_FROM in config
        assert self.WEB_SERVER not in config

    @pytest.mark.parametrize("folder", VISUAL_FOLDERS)
    def test_a_front_end_that_compares_screens_uses_the_shared_visual_config(self, folder: str) -> None:
        assert f"{self.DEFINE}(" in self.text(folder, self.PLAYWRIGHT_CONFIG)

    @pytest.mark.parametrize("folder", FOLDERS)
    def test_the_tsconfig_includes_the_e2e_files(self, folder: str) -> None:
        include = json.loads(self.text(folder, self.TSCONFIG)).get(self.INCLUDE)
        assert isinstance(include, list)
        for entry in self.TSCONFIG_ENTRIES:
            assert entry in include
