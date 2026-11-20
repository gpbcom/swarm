from __future__ import annotations

import re
from typing import Dict, List

from pydantic import JsonValue

from tests.harness.wiring.helpers import read_json


class TestHarnessSettings:
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
