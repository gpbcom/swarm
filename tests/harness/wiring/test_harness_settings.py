from __future__ import annotations

# Standard library imports
import json
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import ClassVar, Dict, List

# Third-party imports
import pytest
from pydantic import JsonValue

# First-party imports
from tests.harness.wiring.helpers import read_json


class TestHarnessSettings:
    VERIFY_DEPS: ClassVar[str] = "pnpm_config_verify_deps_before_run"
    NAME_KEY: ClassVar[str] = "name"
    VERSION_KEY: ClassVar[str] = "version"
    SCRIPTS_KEY: ClassVar[str] = "scripts"
    DEPENDENCIES_KEY: ClassVar[str] = "dependencies"
    SCRIPTS: ClassVar[Dict[str, str]] = {"t": "echo ran"}

    def write_package(self, folder: Path, name: str, dependencies: Dict[str, str]) -> None:
        folder.mkdir(parents=True, exist_ok=True)
        package: Dict[str, JsonValue] = {self.NAME_KEY: name, self.VERSION_KEY: "1.0.0"}
        package[self.SCRIPTS_KEY] = dict(self.SCRIPTS)
        if dependencies:
            package[self.DEPENDENCIES_KEY] = dict(dependencies)
        (folder / "package.json").write_text(json.dumps(package), encoding="utf-8")

    def hook_commands(self, event: str, name: str = "") -> List[Dict[str, JsonValue]]:
        settings = read_json(".claude/settings.json")
        entries = settings.get("hooks", {}).get(event, [])  # type: ignore[attr-defined]
        found: List[Dict[str, JsonValue]] = []
        for entry in entries:
            if name and not re.fullmatch(entry.get("matcher", ""), name):
                continue
            found.extend(entry["hooks"])
        return found

    def test_settings_keep_the_specs_permission_and_the_worktree_base(self) -> None:
        settings = read_json(".claude/settings.json")
        allow = settings["permissions"]["allow"]  # type: ignore[index]
        assert "Bash(python3 .claude/skills/write-specs/scripts/specs.py:*)" in allow
        assert settings["worktree"]["baseRef"] == "head"  # type: ignore[index]

    def test_post_tool_use_formats_edited_files(self) -> None:
        for tool in ("Edit", "Write", "MultiEdit"):
            commands = [
                hook
                for hook in self.hook_commands("PostToolUse", tool)
                if hook.get("type") == "command"
                and "$CLAUDE_PROJECT_DIR" in str(hook.get("command"))
                and ".claude/hooks/format_edited.py" in str(hook.get("command"))
            ]
            assert commands, tool
            assert all(isinstance(hook.get("timeout"), int) for hook in commands)

    def test_subagent_stop_checks_the_touched_layer(self) -> None:
        commands = [
            hook
            for hook in self.hook_commands("SubagentStop")
            if hook.get("type") == "command"
            and "$CLAUDE_PROJECT_DIR" in str(hook.get("command"))
            and ".claude/hooks/check_touched.py" in str(hook.get("command"))
        ]
        assert commands
        assert all(isinstance(hook.get("timeout"), int) for hook in commands)

    def test_pre_tool_use_guards_the_git_commands_of_bash(self) -> None:
        commands = [
            hook
            for hook in self.hook_commands("PreToolUse", "Bash")
            if hook.get("type") == "command" and ".claude/hooks/guard_git.py" in str(hook.get("command"))
        ]
        assert commands
        assert all(isinstance(hook.get("timeout"), int) for hook in commands)

    def test_the_status_line_shows_the_branch_and_the_board(self) -> None:
        settings = read_json(".claude/settings.json")
        status_line = settings["statusLine"]  # type: ignore[index]
        assert status_line["type"] == "command"  # type: ignore[index]
        assert ".claude/scripts/reports/statusline.py" in str(status_line["command"])  # type: ignore[index]

    def test_every_session_runs_pnpm_scripts_without_installing(self) -> None:
        env = read_json(".claude/settings.json").get("env")
        assert isinstance(env, dict)
        assert env.get(self.VERIFY_DEPS) == "warn"

    def test_a_pnpm_script_run_with_the_settings_env_leaves_the_lock_file_alone(self, tmp_path: Path) -> None:
        if shutil.which("pnpm") is None:
            pytest.skip("pnpm is not installed")
        env = read_json(".claude/settings.json").get("env")
        assert isinstance(env, dict)
        (tmp_path / "pnpm-workspace.yaml").write_text('packages:\n  - "*"\n', encoding="utf-8")
        self.write_package(tmp_path, "root", {})
        self.write_package(tmp_path / "a", "a", {})
        self.write_package(tmp_path / "b", "b", {})
        install = ["pnpm", "install", "--offline"]
        subprocess.run(install, cwd=tmp_path, check=True, capture_output=True, timeout=120)
        before = (tmp_path / "pnpm-lock.yaml").read_text(encoding="utf-8")
        self.write_package(tmp_path / "a", "a", {"b": "workspace:*"})
        settings_env = {str(key): str(value) for key, value in env.items()}
        ran = subprocess.run(
            ["pnpm", "--offline", "--filter", "a", "run", "t"],
            cwd=tmp_path,
            capture_output=True,
            text=True,
            env={**os.environ, **settings_env},
            timeout=120,
            check=False,
        )
        assert ran.returncode == 0, ran.stderr
        assert (tmp_path / "pnpm-lock.yaml").read_text(encoding="utf-8") == before
