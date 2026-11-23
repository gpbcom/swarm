from __future__ import annotations

# Standard library imports
import json
import re
from pathlib import Path
from typing import Dict, List, Set

# Third-party imports
import pytest

ROOT = Path(__file__).resolve().parents[3]
REGISTRY = ROOT / ".claude" / "rules" / "enforcement.json"
RULE_FILES = (".claude/rules/specs.md", ".claude/rules/tickets.md")
KINDS = {"test", "script", "hook", "workflow", "agent", "ci"}
RULE_ROW = re.compile(r"^\| \[((?:SPEC|TKT)-\d+)\]\(#")


def rule_ids() -> Set[str]:
    found: Set[str] = set()
    for name in RULE_FILES:
        for line in (ROOT / name).read_text(encoding="utf-8").splitlines():
            match = RULE_ROW.match(line)
            if match:
                found.add(match.group(1))
    return found


def registry() -> Dict[str, List[Dict[str, str]]]:
    loaded: Dict[str, List[Dict[str, str]]] = json.loads(REGISTRY.read_text(encoding="utf-8"))["rules"]
    return loaded


class TestEnforcement:
    def test_every_rule_names_how_it_is_enforced(self) -> None:
        missing = sorted(rule_ids() - set(registry()))
        assert missing == [], f"rules without an entry in {REGISTRY.name}: {missing}"

    def test_the_registry_names_no_rule_that_does_not_exist(self) -> None:
        assert sorted(set(registry()) - rule_ids()) == []

    @pytest.mark.parametrize("rule", sorted(rule_ids()))
    def test_each_rule_has_an_enforcer_that_exists(self, rule: str) -> None:
        enforcers = registry().get(rule, [])
        assert enforcers, f"{rule} has no enforcer"
        for enforcer in enforcers:
            assert enforcer["kind"] in KINDS, enforcer
            assert enforcer["what"].strip(), enforcer
            assert (ROOT / enforcer["path"]).exists(), f"{rule}: {enforcer['path']} does not exist"
            if enforcer["kind"] == "agent":
                assert enforcer["path"].startswith(".claude/agents/"), enforcer

    @pytest.mark.parametrize("rule", sorted(rule_ids()))
    def test_each_rule_is_enforced_by_more_than_reading_alone(self, rule: str) -> None:
        kinds = {enforcer["kind"] for enforcer in registry().get(rule, [])}
        assert kinds - {"agent"}, f"{rule} is only checked by reading: add a test or a script"
